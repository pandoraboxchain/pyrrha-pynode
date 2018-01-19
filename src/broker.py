import sys
import logging
import time
from threading import Thread
from os.path import exists
from scrypt import decrypt
from typing import Union

from patterns.singleton import *
from eth.eth_connector import EthConnector
from node.worker_node import *
from job.cognitive_job import *
from processor.processor import *
from webapi.webapi import *


class Broker(Singleton, Thread, WorkerNodeDelegate, CognitiveJobDelegate, ProcessorDelegate):
    """
    Broker manages all underlying services/threads and arranges communications between them. Broker directly manages
    WebAPI and Ethereum threads and provides delegate interfaces for capturing their output via callback functions.
    This is done via implementing `EthDelegate` and `WebDelegate` abstract classes.
    """

    ##
    # Initialization
    ##

    def __init__(self, eth_server: str, abi_path: str, pandora: str, node: str, vault: str,
                 ipfs_server: str, ipfs_port: int, data_dir: str, use_hooks: bool = False):
        """
        Instantiates Broker object and its members, but does not initiates them (network interfaces are not created/
        bind etc). Broker follows two-step initialization pattern (`Broker(...)` followed by `broker.run` call.

        :param config: Configuration named tuple `BrokerConfig` containing also configuration of all nested services
        (WebAPI, Ethereum connector)
        """

        # Calling singleton init preventing repeated class instantiation
        Singleton.__init__(self)
        Thread.__init__(self, daemon=True)

        # Initializing logger object
        self.logger = logging.getLogger("broker")

        # Saving config
        self.eth_server = eth_server
        self.abi_path = abi_path
        self.vault = vault
        self.ipfs_server = ipfs_server
        self.ipfs_port = ipfs_port
        self.data_dir = data_dir

        # Instantiating services objects
        EthConnector.server = self.eth_server
        self.pandora = EthConnector(address=pandora,
                                    abi_path=self.abi_path, abi_file='PandoraHooks' if use_hooks else 'Pandora')
        self.node = WorkerNode(delegate=self, address=node, abi_path=self.abi_path, abi_file='WorkerNode')
        self.jobs = {}
        self.processors = {}

        # self.api = WebAPI(config=self.config.webapi, delegate=self)

    def connect(self, password: str) -> bool:
        """
        Starts all necessary interfaces (WebAPI, Ethereum and its underlying interfaces). Fails if any of them failed.

        :return: Success or failure status as a bool value
        """

        # Trying to bind web api port (to fail early before trying everything else more complex)
        # self.logger.info("Starting api...")
        # if not self.api.bind():
        #     self.logger.error("Can't bind to Web API port, shutting down")
        #     return False

        # Since all necessary network environments are available for now we can run the services as a separate threads
        # self.api.run()

        self.logger.info("Opening vault file %s with private key", self.vault)
        if not exists(self.vault):
            self.logger.error("Ethereum account vault file %s is not present, exiting", self.vault)
            return False

        with open(self.vault, 'rb') as file:
            cypher = file.read()
            pri_key = decrypt(cypher, password)
        self.logger.info("Private key successfully read")

        try:
            result = EthConnector.connect(pri_key)
            result &= self.pandora.init_contract() if result else False
            result &= self.node.init_contract() if result else False
        except Exception as ex:
            self.logger.error("Exception initializing contracts: %s", type(ex))
            self.logger.error(ex.args)
            return False
        if result is not True:
            self.logger.error("Unable to start broker, exiting")
            return False

        job_address = self.node.cognitive_job_address()
        self.logger.info("Initializing cognitive job contract for address %s", job_address)
        if job_address is not None:
            if job_address in self.jobs:
                raise Exception('Internal inconsistency: cognitive job is already initialized')
            result = self.__init_cognitive_job(job_address)

        result &= self.node.bootstrap() if result else False

        if result is not True:
            self.logger.error("Unable to start broker, exiting")
            return False

        self.logger.info("Broker started successfully")

        super().start()
        self.node.join()

        return True

    ##
    # Private supplementary functions
    ##

    def __init_cognitive_job(self, job_address: str) -> bool:
        """Supplementary private method used for instantiating `CognitiveJob` contract either on daemon launch
        (if associated WorkerNode contract already has an assigned job) or upon new cognitive job assignment at
        runtime

        :param job_address: Address of CognitiveJob contract in Ethereum network

        :returns: Success or failure boolean value"""

        try:
            job = CognitiveJob(delegate=self, address=job_address, abi_path=self.abi_path, abi_file='CognitiveJob')
            result = job.init_contract()
            result &= job.bootstrap() if result else False
        except Exception as ex:
            self.logger.error("Exception initializing cognitive job contract: %s", type(ex))
            self.logger.error(ex.args)
            return False
        if result is not True:
            return False
        self.jobs[job_address] = job
        return True

    def __init_processor(self, node: WorkerNode) -> Processor:
        """Supplementrary private method used for instantiating `Processor` class either on new validation or
        cognition task

        :param node: `WorkerNode` instance (reserved for the future use when pynode will be able to connect
        multiple WorkerNode contracts)

        :returns: `Processor` instance associated with a given pair or WorkerNode and CognitiveJob contracts"""

        job_address = node.cognitive_job_address()
        node_address = node.address
        processor_id = '%s:%s' % (node_address, job_address)

        job = self.jobs[job_address]
        workers = job.workers()
        batch = None
        for idx, w in enumerate(workers):
            if self.node.address is w:
                batch = idx
                break
        if batch is None:
            raise Exception("Can't determine worker this node batch number")

        if processor_id in self.processors:
            return self.processors[processor_id]

        processor = Processor(id=processor_id, ipfs_server=self.ipfs_server, ipfs_port=self.ipfs_port,
                              abi_path=self.abi_path, data_dir=self.data_dir, delegate=self)
        self.processors[processor_id] = processor
        processor.run()
        processor.prepare(kernel=job.kernel_address(), dataset=job.dataset_address(), batch=batch)
        return processor

    ##
    # Delegate methods
    ##

    # WorkerNodeDelegate

    def create_cognitive_job(self, job_address: str):
        if job_address in self.jobs:
            return
        self.logger.info("Initializing cognitive job contract for address %s", job_address)
        if self.__init_cognitive_job(job_address) is False:
            self.logger.error("Error initializing cognitive job for address %s", job_address)

    def start_validating(self, node: WorkerNode):
        self.logger.info("Starting validating data")
        try:
            processor = self.__init_processor(node)
        except:
            self.processor_load_failure(None)
            return
        processor.load()

    def start_computing(self, node: WorkerNode):
        self.logger.info("Starting computing cognitive job")
        try:
            processor = self.__init_processor(node)
        except:
            self.processor_computing_failure(None)
            return
        processor.compute()

    # CognitiveJobDelegate

    def terminate_job(self, job: CognitiveJob):
        # TODO: Implement
        pass

    # ProcessorDelegate

    def processor_load_complete(self, processor_id: str):
        self.node.transact_accept_valid_data()

    def processor_load_failure(self, processor_id: Union[str, None]):
        self.node.transact_report_invalid_data()

    def processor_computing_complete(self, processor_id: str, results_file: str):
        self.node.transact_provide_results(results_file)

    def processor_computing_failure(self, processor_id: Union[str, None]):
        self.logger.critical("Can't complete computing, exiting in order to reboot and try to repeat the work")
        sys.exit(1)
