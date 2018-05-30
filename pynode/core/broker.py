import sys
import logging
import json
import time

from threading import Thread
from typing import Union, Callable

from integration.eth_service import EthService
from integration.integration.eth_connector import EthConnector
from integration.ipfs_service import IpfsService
from integration.integration.ipfs_connector import IpfsConnector

from core.manager import Manager
from service.tools.key_tools import KeyTools

from core.node.worker_node import WorkerNode, WorkerNodeDelegate
from core.job.cognitive_job import CognitiveJob

from core.patterns.singleton import Singleton
from core.patterns.pynode_logger import LogSocketHandler
from core.patterns.exceptions import CriticalTransactionError

from core.processor.processor import Processor, ProcessorDelegate


class Broker(Thread, Singleton, WorkerNodeDelegate, ProcessorDelegate):
    """
    Broker manages all underlying services/threads and arranges communications between them. Broker directly manages
    WebAPI and Ethereum threads and provides delegate interfaces for capturing their output via callback functions.
    This is done via implementing `EthDelegate` and `WebDelegate` abstract classes.
    """
# ----------------------------------------------------------------------------------------------------------
# Initialization
# ----------------------------------------------------------------------------------------------------------
    def __init__(self, eth_server: str, abi_path: str,
                 pandora: str,
                 node: str,
                 ipfs_server: str, ipfs_port: int, data_dir: str):
        Broker.get_instance()
        Thread.__init__(self, daemon=True)

        # Initializing logger object
        self.logger = logging.getLogger("Broker")
        self.logger.addHandler(LogSocketHandler.get_instance())
        self.manager = Manager.get_instance()
        self.mode = self.manager.launch_mode

        # Saving starter configs
        self.eth_server = eth_server
        self.abi_path = abi_path
        self.pandora = pandora
        self.node = node
        self.ipfs_server = ipfs_server
        self.ipfs_port = ipfs_port
        self.data_dir = data_dir

        # Init empty container for pandora
        self.pandora_container = None

        # Init empty containers for worker node
        self.worker_node_container = None
        self.worker_node_state_machine = None
        self.worker_node_event_thread = None

        # Init empty containers for job
        self.job_address = None
        self.job_container = None
        self.job_state_machine = None
        self.job_state_event_thread = None

        # Init empty jobs and processor
        self.jobs = {}
        self.processors = {}

        # init connectors
        self.eth = EthService(strategic=EthConnector())
        self.ipfs = IpfsService(strategic=IpfsConnector())

        self.local_password = None
        self.key_tool = KeyTools()
        print('Pandora broker initialize success')


# ----------------------------------------------------------------------------------------------------------
# Base connection and start pynode
# ----------------------------------------------------------------------------------------------------------
    def connect(self) -> bool:
        if self.eth is not None:
            # init base contracts containers
            self.pandora_container = self.eth.init_contract(server_address=self.manager.eth_host,
                                                            contract_address=self.pandora,
                                                            contract_abi=self.manager.eth_pandora_contract)
            self.logger.info('Pandora contract initialized success on address : ' + self.pandora)
            self.worker_node_container = self.eth.init_contract(server_address=self.manager.eth_host,
                                                                contract_address=self.node,
                                                                contract_abi=self.manager.eth_worker_contract)
            self.logger.info('Worker contract initialized success on address : ' + self.node)

            # init worker contract owner account
            if self.key_tool.check_vault():
                self.logger.info('Account vault is located')
                vault_data = self.key_tool.obtain_key(self.manager.vault_key)
                # split data to pass and p_key
                self.local_password = vault_data.split("_", 1)[0]
                vault_account = vault_data.split("_", 1)[0]
                local_p_key = vault_data.split("_", 1)[1]
                if (vault_account.lower() in self.manager.eth_worker_node_account.lower()) and (local_p_key is not ''):
                    self.logger.info('Vault check success')
                else:
                    self.logger.info('Unable to unlock account vault.')
                    self.logger.info('Please provide pynode configuration.')
                    return False
            else:
                self.logger.info('Unable to locate account vault.')
                self.logger.info('Please provide pynode configuration.')
                return False

            self.logger.info('Worker account determination success')
            # init worker node state machine and get current state
            self.worker_node_state_machine = WorkerNode(contract_container=self.worker_node_container,
                                                        delegate=self,
                                                        address=self.node,
                                                        contract=self.manager.eth_worker_contract)
            # bind worker node states listener thread
            filter_on_worker = self.worker_node_container.events.StateChanged.createFilter(fromBlock='latest')
            self.worker_node_event_thread = Thread(target=self.worker_filter_thread_loop,
                                                   args=(filter_on_worker, 2),
                                                   daemon=True)
            self.worker_node_event_thread.start()
            status = self.worker_node_event_thread.is_alive()
            self.logger.info('Event listener for worker node creation startup success, alive : ' + str(status))
            self.logger.info('Worker node state event thread listener initialize success')

            # process current worker node state after worker node event thread is initialized
            current_worker_node_state = self.worker_node_state_machine.process_state()
            self.logger.info('Worker node state machine initialized success with state : '
                             + str(current_worker_node_state))

            # start main broker thread
            super().start()
            self.logger.info("Broker started successfully")
            # ----------------------------------------------------------------------------------
            # JOIN WORKER EVENTS CHANGE LISTENER to main process
            # ----------------------------------------------------------------------------------
            if self.mode == "0":  # join threads only in production mode
                self.worker_node_event_thread.join()
                if self.job_state_event_thread:
                    self.job_state_event_thread.join()
            return True
        else:
            self.logger.info('Pynode eth connector not instantiated. exit')
            return False

    def disconnect(self):
        super().join()

# ----------------------------------------------------------------------------------------------------------
# JOB and PROCESSOR initialization
# ----------------------------------------------------------------------------------------------------------
    # todo job address is necessary ADD it to method call parameters
    def init_cognitive_job(self) -> bool:
        self.manager.job_contract_address = self.job_address
        self.job_container = self.eth.init_contract(server_address=self.manager.eth_host,
                                                    contract_address=self.job_address,
                                                    contract_abi=self.manager.eth_cognitive_job_contract)
        self.logger.info('Job contract initialized success on address : ' + self.job_address)
        self.job_state_machine = CognitiveJob(contract_container=self.job_container,
                                              delegate=self,
                                              address=self.job_address,
                                              contract=self.manager.eth_cognitive_job_contract)
        current_job_state = self.job_state_machine.process_state()
        self.logger.info('Cognition job state machine initialized success with state : '
                         + str(current_job_state))
        self.jobs[self.job_address] = self.job_container

        filter_on_job = self.job_container.events.StateChanged.createFilter(fromBlock='latest')
        self.job_state_event_thread = Thread(target=self.job_filter_thread_loop,
                                             args=(filter_on_job, 2),
                                             daemon=True)
        self.job_state_event_thread.start()
        status = self.job_state_event_thread.is_alive()
        self.logger.info('Event listener for job states creation startup success, alive : ' + str(status))
        self.logger.info('Cognitive job state event thread listener initialize success')
        return True

    # TODO for multiprocess cognition need to rebuild processor init flow
    def init_processor(self) -> Processor:
        # get kernel and dataset
        # prepare processor for calculating data
        if self.ipfs is not None:
            # init job container if empty
            if not self.job_container:
                self.job_address = self.worker_node_container.call().activeJob()
                self.init_cognitive_job()

            try:
                kernel_address = self.job_container.call().kernel()
                dataset_address = self.job_container.call().dataset()
            except Exception as ex:
                self.logger.error("Exception initializing job internal contract")
                self.logger.error(ex.args)
                return False

            self.logger.info('Start determinate kernel and dataset contracts')
            try:
                kernel_container = self.eth.init_contract(server_address=self.manager.eth_host,
                                                          contract_address=kernel_address,
                                                          contract_abi=self.manager.eth_kernel_contract)
                self.logger.info('Kernel contract instantiated success')
                dataset_container = self.eth.init_contract(server_address=self.manager.eth_host,
                                                           contract_address=dataset_address,
                                                           contract_abi=self.manager.eth_dataset_contract)
                self.logger.info('Dataset contract instantiated success')
            except Exception as ex:
                self.logger.error("Exception contract initializing")
                self.logger.error(ex.args)

            # get kernel and dataset addresses
            kernel_ipfs_address = kernel_container.call().ipfsAddress()
            dataset_ipfs_address = dataset_container.call().ipfsAddress()
            self.logger.info('Kernel ipfs address : ' + str(kernel_ipfs_address))
            self.logger.info('Dataset ipfs address : ' + str(dataset_ipfs_address))

            # determinate batch for current job
            job = self.jobs[self.job_address]
            workers = []
            workers_count = job.call().activeWorkersCount()
            for w in range(0, workers_count):
                workers.append(job.call().activeWorkers(w).lower())
            batch = None
            for idx, w in enumerate(workers):
                if self.node.lower() == w.lower():
                    batch = idx
                    break
            if batch is None:
                raise Exception("Can't determine this node batch number")
            # prepare ipfs
            self.logger.info('Start loading files data...')
            self.ipfs.connect(server=self.ipfs_server,
                              port=self.ipfs_port,
                              data_dir=self.data_dir)
            self.logger.info('IPFS connection instantiated success')
            # load kernel and dataset root files
            self.ipfs.download_file(kernel_ipfs_address.decode("utf-8"))
            self.logger.info('Kernel datafile download success...')
            self.ipfs.download_file(dataset_ipfs_address.decode("utf-8"))
            self.logger.info('Dataset datafile download success...')

            processor_id = '%s:%s' % (self.node, self.job_address)
            # processor initialization
            processor = Processor(ipfs_api=self.ipfs,
                                  processor_id=processor_id,
                                  delegate=self)
            self.processors[processor_id] = processor
            processor.run()
            processor.prepare(kernel_file=self.read_file(kernel_ipfs_address),
                              dataset_file=self.read_file(dataset_ipfs_address),
                              batch=batch)
            return processor

    @staticmethod
    def read_file(file_address) -> dict:
        with open(file_address) as json_file:
            info = json.load(json_file)
        return info

    @staticmethod
    def check_job_address(job_address: str) -> str:
        result = job_address
        trimmed_address = job_address.replace('0', '')
        if trimmed_address == 'x':
            result = None
        return result

# ----------------------------------------------------------------------------------------------------------
# Broker listeners for state table change states processing
# ----------------------------------------------------------------------------------------------------------
    # worker node state filter thread loop
    def worker_filter_thread_loop(self, event_filter, poll_interval):
        while True:
            try:
                for event in event_filter.get_all_entries():
                    self.on_worker_node_state_change(event)
                time.sleep(poll_interval)
            except Exception as ex:
                if isinstance(ex.args, tuple):
                    if len(ex.args) > 0:
                        message = ex.args[0]
                        if 'filter not found' in str(message):
                            # sometimes for unknown reason filter drops on eth node, so recreate it
                            event_filter = self.worker_node_container.events.StateChanged.createFilter(fromBlock='latest')
                else:
                    self.logger.info('Exception on worker event handler.')
                    self.logger.info(ex.args)

    def on_worker_node_state_change(self, event: dict):
        worker_state_table = self.worker_node_state_machine.state_table
        state_old = event['args']['oldState']
        state_new = event['args']['newState']
        self.logger.info("Contract WorkerNode changed its state from %s to %s",
                         worker_state_table[state_old].name,
                         worker_state_table[state_new].name)
        self.worker_node_state_machine.state = state_new

    # job state filter loop
    def job_filter_thread_loop(self, event_filter, pool_interval):
        while True:
            try:
                for event in event_filter.get_all_entries():
                    self.on_cognitive_job_state_change(event)
                time.sleep(pool_interval)
            except Exception as ex:
                if isinstance(ex.args, tuple):
                    if len(ex.args) > 0:
                        message = ex.args[0]
                        if 'filter not found' in str(message):
                            # sometimes for unknown reason filter drops on eth node, so recreate it
                            event_filter = self.job_container.events.StateChanged.createFilter(fromBlock='latest')
                else:
                    self.logger.info('Exception on job event handler.')
                    self.logger.info(ex.args)

    def on_cognitive_job_state_change(self, event: dict):
        job_state_table = self.job_state_machine.state_table
        state_old = event['args']['oldState']
        state_new = event['args']['newState']
        self.logger.info("Contract Cognitive job changed its state from %s to %s",
                         job_state_table[state_old].name,
                         job_state_table[state_new].name)
        self.job_state_machine.state = state_new


# ----------------------------------------------------------------------------------------------------------
# Worker node delegate methods
# ----------------------------------------------------------------------------------------------------------
    def create_cognitive_job(self):
        if self.job_container:
            return
        job_address = self.worker_node_container.call().activeJob()
        if self.check_job_address(job_address) is None:
            self.logger.info("Job address is empty, cant determinate job")
            return
        if job_address in self.jobs:
            return
        self.logger.info("Initializing cognitive job contract for address %s", job_address)
        self.job_address = job_address
        if self.init_cognitive_job() is False:
            self.logger.error("Error initializing cognitive job for address %s", job_address)

    def start_validating(self):
        self.logger.info("Starting validating data")
        try:
            processor = self.init_processor()
        except Exception as ex:
            self.logger.error("Error during processor initialization: %s", type(ex))
            self.logger.error(ex.args)
            self.processor_load_failure(None)
            return
        processor.load()

    def start_computing(self):
        self.logger.info("Starting computing cognitive job")
        if not self.processors:  # if processors is empty init it
            try:
                processor = self.init_processor()
            except Exception as ex:
                self.logger.error("Error during processor initialization: %s", type(ex))
                self.logger.error(ex.args)
                self.processor_computing_failure(None)
                return
            # start computing after processor init
            processor.compute()
        else:
            list(self.processors.values())[0].compute()

    def state_transact(self, name: str, *result_file):
        self.logger.info("Transact to worker node : " + name)
        private_key = self.key_tool.obtain_key(self.manager.vault_key).split("_", 1)[1]
        try:
            nonce = self.worker_node_container.web3.eth.getTransactionCount(self.manager.eth_worker_node_account)
            raw_transaction = None
            if name in 'alive':
                raw_transaction = self.worker_node_container.functions.alive() \
                    .buildTransaction({
                        'from': self.manager.eth_worker_node_account,
                        'nonce': nonce})
            if name in 'acceptAssignment':
                raw_transaction = self.worker_node_container.functions.acceptAssignment() \
                    .buildTransaction({
                        'from': self.manager.eth_worker_node_account,
                        'nonce': nonce})
            if name in 'processToDataValidation':
                raw_transaction = self.worker_node_container.functions.processToDataValidation() \
                    .buildTransaction({
                        'from': self.manager.eth_worker_node_account,
                        'nonce': nonce})
            if name in 'reportInvalidData':
                raw_transaction = self.worker_node_container.functions.reportInvalidData() \
                    .buildTransaction({
                        'from': self.manager.eth_worker_node_account,
                        'nonce': nonce})
            if name in 'acceptValidData':
                raw_transaction = self.worker_node_container.functions.acceptValidData() \
                    .buildTransaction({
                        'from': self.manager.eth_worker_node_account,
                        'nonce': nonce})
            if name in 'processToCognition':
                raw_transaction = self.worker_node_container.functions.processToCognition() \
                    .buildTransaction({
                        'from': self.manager.eth_worker_node_account,
                        'nonce': nonce})
            if name in 'provideResults':
                raw_transaction = self.worker_node_container.functions.provideResults(str.encode(result_file[0])) \
                    .buildTransaction({
                        'from': self.manager.eth_worker_node_account,
                        'nonce': nonce})

            if raw_transaction is not None:
                signed_transaction = self.worker_node_container.web3.eth.account.signTransaction(raw_transaction,
                                                                                                 private_key)
                tx_hash = self.worker_node_container.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
                self.logger.info('TX_HASH : ' + tx_hash.hex())
                self.logger.info('Waiting for receipt...')
                transaction_receipt = self.worker_node_container.web3.eth.waitForTransactionReceipt(tx_hash,
                                                                                                    timeout=300)
                self.logger.info('TX_RECEIPT : ' + str(transaction_receipt))
                self.logger.info('TRANSACTION_STATUS = ' + str(transaction_receipt['status']))
            else:
                self.logger.info('Unknown state transaction. Skip.')
        except Exception as ex:
            self.logger.error("Error executing %s transaction: %s", name, type(ex))
            self.logger.error(ex.args)
            raise CriticalTransactionError(name)
        return

# ----------------------------------------------------------------------------------------------------------
# Cognitive job delegate methods
# ----------------------------------------------------------------------------------------------------------
    def terminate_job(self, job: CognitiveJob):
        pass

    def transact(self, name: str, cb: Callable):
        pass

# ----------------------------------------------------------------------------------------------------------
# Processor delegate methods
# ----------------------------------------------------------------------------------------------------------
    def processor_load_complete(self, processor_id: str):
        self.logger.info('Processor loading complete.')
        self.logger.info('Confirming data validness')
        self.state_transact('acceptValidData')

    def processor_load_failure(self, processor_id: Union[str, None]):
        self.logger.info('Processor loading fail.')
        self.logger.info('Reporting invalid data')
        self.state_transact('reportInvalidData')

    def processor_computing_complete(self, processor_id: str, results_file: str):
        self.logger.info('Processor computing complete.')
        self.logger.info('Providing results')
        self.logger.info('Result file address : ' + results_file)
        self.manager.set_complete_reset()
        self.state_transact('provideResults', results_file)

    def processor_computing_failure(self, processor_id: Union[str, None]):
        self.logger.critical("Can't complete computing, exiting in order to reboot and try to repeat the work")
        sys.exit(1)


