import logging
import time
from threading import Thread
from os.path import exists
from scrypt import decrypt

from patterns.singleton import *
from eth.eth_connector import EthConnector
from node.worker_node import *
from job.cognitive_job import *
from processor.processor import *
from webapi.webapi import *


class Broker (Singleton, Thread, WorkerNodeDelegate, CognitiveJobDelegate, ProcessorDelegate):
    """
    Broker manages all underlying services/threads and arranges communications between them. Broker directly manages
    WebAPI and Ethereum threads and provides delegate interfaces for capturing their output via callback functions.
    This is done via implementing `EthDelegate` and `WebDelegate` abstract classes.
    """

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
        if job_address is not None:
            result = self.init_cognitive_job(job_address)

        result &= self.node.bootstrap() if result else False

        if result is not True:
            self.logger.error("Unable to start broker, exiting")
            return False

        self.logger.info("Broker started successfully")

        super().start()

        return True

    def init_cognitive_job(self, job_address: str) -> bool:
        self.logger.info("Initializing cognitive job contract for address %s", job_address)
        if job_address in self.jobs:
            raise Exception('Internal inconsistency: cognitive job is already initialized')
        return self.__init_cognitive_job(job_address)

    def create_cognitive_job(self, job_address: str):
        if job_address in self.jobs:
            return
        self.logger.info("Initializing cognitive job contract for address %s", job_address)
        if self.__init_cognitive_job(job_address) is False:
            self.logger.error("Error initializing cognitive job for address %s", job_address)

    def __init_cognitive_job(self, job_address: str) -> bool:
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

    def start_validating(self, node: WorkerNode):
        self.logger.info("Starting validating data for cognitive job %s...", job_address)
        processor = self.__init_processor(node)
        processor.load()

    def start_computing(self, node: WorkerNode):
        self.logger.info("Starting computing cognitive job %s...", job_address)
        processor = self.__init_processor(node)
        processor.compute()

    def __init_processor(self, node: WorkerNode) -> Processor:
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

        processor = Processor(ipfs_server=self.ipfs_server, ipfs_port=self.ipfs_port,
                              abi_path=self.abi_path, data_dir=self.data_dir, delegate=self)
        self.processors[processor_id] = processor
        processor.run()
        processor.prepare(kernel=job.kernel_address(), dataset=job.dataset_address(), batch=batch)
        return processor

    def terminate_job(self, job: CognitiveJob):
        # TODO: Implement
        pass
