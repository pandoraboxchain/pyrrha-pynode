import sys
import logging
import json
import time
import os
import subprocess

from threading import Thread
from typing import Union, Callable

from web3.gas_strategies.time_based import medium_gas_price_strategy

from integration.eth_service import EthService
from integration.integration.eth_connector import EthConnector
from integration.ipfs_service import IpfsService
from integration.integration.ipfs_connector import IpfsConnector

from core.manager import Manager
from service.tools.key_tools import KeyTools

from core.node.worker_node import WorkerNodeDelegate
from core.node.worker_node_thread import WorkerNodeStateMachineThread, WorkerNodeStateDelegate

from core.job.cognitive_job import CognitiveJob
from core.patterns.singleton import Singleton
from core.patterns.pynode_logger import LogSocketHandler
from core.processor.processor import Processor, ProcessorDelegate
from core.processor.entities.kernel import ProgressDelegate


class Broker(Thread, Singleton, WorkerNodeDelegate, WorkerNodeStateDelegate, ProcessorDelegate, ProgressDelegate):
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
        self.logger.setLevel(logging.INFO)
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

        # initial filtering current block number
        self.current_block_number = 0

        # Init empty container for pandora
        self.pandora_container = None
        # Init empty container for cognitive job manager
        self.job_controller = None
        self.job_controller_address = None
        self.job_controller_container = None

        # Init empty containers for worker node
        self.worker_node_container = None
        self.worker_node_state_machine = None
        self.worker_node_event_thread = None

        # Init empty containers for job
        self.job_id_hex = None
        self.job_container = None
        self.job_state_machine = None
        self.job_state_event_thread = None
        self.job_state_thread_flag = True

        # Init empty jobs and processor
        self.jobs = {}
        self.processors = {}

        # init connectors
        self.eth = EthService(strategic=EthConnector())
        self.ipfs = IpfsService(strategic=IpfsConnector())

        # init progress delegate
        self.send_progress = False
        self.start_training_time = None
        self.finish_training_time = None
        self.current_epoch = None
        self.start_epoch_time = None
        self.finish_epoch_time = None
        self.time_per_epoch = None
        self.sends_count = 1
        self.send_progress_interval = 300  # set to 5min by default

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

            self.job_controller_address = self.pandora_container.call().jobController()
            self.logger.info('Pandora cognitive job controller address : ' + self.pandora)
            self.job_controller_container = self.eth.init_contract(server_address=self.manager.eth_host,
                                                                   contract_address=self.job_controller_address,
                                                                   contract_abi=self.manager.eth_job_controller_contract)
            self.logger.info('Pandora cognitive job controller initialize success')

            self.worker_node_container = self.eth.init_contract(server_address=self.manager.eth_host,
                                                                contract_address=self.node,
                                                                contract_abi=self.manager.eth_worker_contract)
            self.logger.info('Worker contract initialized success on address : ' + self.node)
            self.worker_node_container.web3.eth.setGasPriceStrategy(medium_gas_price_strategy)
            self.logger.info('Set gas price strategy to -> medium_gas_price_strategy')

            # init worker contract owner account
            if self.key_tool.check_vault():
                self.logger.info('Account vault is located')
                vault_data = self.key_tool.obtain_key(self.manager.vault_key)
                # split data to pass and p_key
                try:
                    self.local_password = vault_data.split("_", 1)[0]
                    vault_account = vault_data.split("_", 1)[0]
                    local_p_key = vault_data.split("_", 1)[1]
                    if (vault_account.lower() in self.manager.eth_worker_node_account.lower()) and (local_p_key is not ''):
                        self.logger.info('Vault check success')
                    else:
                        self.logger.info('Unable to unlock account vault.')
                        self.logger.info('Please provide pynode configuration.')
                        return False
                except Exception:
                    self.logger.info('Exception on unlock account vault.')
                    return False
            else:
                self.logger.info('Unable to locate account vault.')
                self.logger.info('Please provide pynode configuration.')
                return False

            self.logger.info('Worker account determination success')
            self.worker_node_state_machine = WorkerNodeStateMachineThread(contract_container=self.worker_node_container,
                                                                          delegate=self,
                                                                          address=self.node,
                                                                          contract=self.manager.eth_worker_contract,
                                                                          state_delegate=self)
            self.logger.info('Event listener for worker node creation startup success, alive : '
                             + str(self.worker_node_state_machine.alive()))
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
                self.worker_node_state_machine.get_worker_node_event_thread().join()
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
    # job address is necessary ADD it to method call parameters
    def init_cognitive_job(self) -> bool:
        if self.job_id_hex not in self.jobs:  # to avoid double init
            self.job_state_machine = CognitiveJob(job_controller_container=self.job_controller_container,
                                                  delegate=self)
            current_job_state = self.job_state_machine.process_state(job_id_hex=self.job_id_hex)
            self.logger.info('Cognition job state machine initialized success with state : '
                             + str(current_job_state))
            self.jobs[self.job_id_hex] = self.job_id_hex  # set job index to fobs list

            # job state loop init
            self.job_state_thread_flag = True
            filter_on_job = self.job_controller_container.events.JobStateChanged.createFilter(fromBlock='latest')
            self.job_state_event_thread = Thread(target=self.job_filter_thread_loop,
                                                 args=(filter_on_job, 2),
                                                 daemon=True)
            self.job_state_event_thread.start()
            status = self.job_state_event_thread.is_alive()
            self.logger.info('Event listener for job states on job controller creation startup success, alive : '
                             + str(status))
            self.logger.info('Cognitive job state event thread listener initialize success')
        return True

    # TODO for multiprocess cognition need to rebuild processor init flow
    def init_processor(self) -> Processor:
        # get kernel and dataset
        # prepare processor for calculating data
        if self.ipfs is not None:
            # init job container if empty
            if not self.job_id_hex:
                self.job_id_hex = self.worker_node_container.web3.toHex(self.worker_node_container.call().activeJob())
                self.init_cognitive_job()

            try:
                kernel_address = self.job_controller_container.call().getCognitiveJobDetails(self.job_id_hex)[0]
                dataset_address = self.job_controller_container.call().getCognitiveJobDetails(self.job_id_hex)[1]
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
            workers = self.job_controller_container.call().getCognitiveJobDetails(self.job_id_hex)[4]
            batch = None
            for idx, w in enumerate(workers):
                if self.node.lower() == w.lower():
                    batch = idx
                    self.logger.info('BATCH_INDEX : ' + str(batch))
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

            processor_id = '%s:%s' % (self.node, self.job_id_hex)
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

    def check_job_id(self, job_address: str) -> str:
        result_hex = self.worker_node_container.web3.toHex(job_address)
        job_address = result_hex
        trimmed_address = job_address.replace('0', '')
        if trimmed_address == 'x':
            result_hex = None
        return result_hex

# ----------------------------------------------------------------------------------------------------------
# Broker listeners for state table change states processing
# ----------------------------------------------------------------------------------------------------------
    def on_worker_node_state_change(self, event: dict):
        worker_state_table = self.worker_node_state_machine.state_table()
        state_old = event['args']['oldState']
        state_new = event['args']['newState']
        self.logger.info("Contract WorkerNode changed its state from %s to %s",
                         worker_state_table[state_old].name,
                         worker_state_table[state_new].name)
        self.worker_node_state_machine.state(state_new)

    # job state filter loop
    def job_filter_thread_loop(self, event_filter, pool_interval):
        while self.job_state_thread_flag:
            try:
                if event_filter:
                    for event in event_filter.get_new_entries():
                        event_job_id = self.worker_node_container.web3.toHex(event['args']['jobId'])
                        if event_job_id == self.job_id_hex:
                            self.on_cognitive_job_state_change(event)
                    time.sleep(pool_interval)
                else:
                    # https://github.com/ethereum/web3.py/issues/354
                    event_filter = self.job_container.events.StateChanged.createFilter(fromBlock='latest')
            except Exception as ex:
                self.logger.info('Exception on job event handler.')
                self.logger.info(ex.args)

    def on_cognitive_job_state_change(self, event: dict):
        job_state_table = self.job_state_machine.state_table
        state_old = event['args']['oldState']
        state_new = event['args']['newState']
        self.logger.info("Contract Cognitive job changed its state from %s to %s",
                         job_state_table[state_old].name,
                         job_state_table[state_new].name)
        # strange behavior of states (on TESLA MACHINE)
        self.job_state_machine.state = state_new


# ----------------------------------------------------------------------------------------------------------
# Worker node delegate methods
# ----------------------------------------------------------------------------------------------------------
    def create_cognitive_job(self):
        self.logger.info('CALL - create_cognitive_job')
        # if job_container currently initialized skip initialization (optimize job initialization)
        # job container assigns to None value on job complete
        if self.job_container:
            self.logger.info('Job container inited. return')
            return
        job_id = self.worker_node_container.call().activeJob()
        if self.check_job_id(job_id) is None:
            self.logger.info("Job ID is invalid, cant determinate job")
            return
        self.job_id_hex = self.worker_node_container.web3.toHex(job_id)
        self.manager.eth_job_id_hex = self.worker_node_container.web3.toHex(job_id)
        self.logger.info("Initializing cognitive job contract for ID %s", self.job_id_hex)
        if self.init_cognitive_job() is False:
            self.logger.error("Error initializing cognitive job for ID %s", self.job_id_hex)

    def start_validating(self):
        self.logger.info('CALL - start_validating')
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
        self.logger.info('CALL - start_computing')
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
            if processor:
                processor.compute()
            # if processor init false terminate job
        else:
            list(self.processors.values())[0].compute()

    def state_transact(self, name: str, *result_file):
        self.logger.info("Transact to worker node : " + name)
        private_key = self.key_tool.obtain_key(self.manager.vault_key).split("_", 1)[1]
        tx_status = 0
        while tx_status == 0:
            try:
                checksum_worker_node_account = self.worker_node_container.web3.toChecksumAddress(
                    self.manager.eth_worker_node_account)
                nonce = self.worker_node_container.web3.eth.getTransactionCount(checksum_worker_node_account,
                                                                                "pending")
                self.logger.info('Calculate gas estimation...')
                gas_estimation = self.worker_node_container.web3.eth.generateGasPrice()
                gas_estimation = int(gas_estimation + gas_estimation/2)
                gas_price = self.worker_node_container.web3.eth.gasPrice
                self.logger.info('Gas estimated : ' + str(gas_estimation))
                raw_transaction = None
                if name in 'alive':
                    raw_transaction = self.worker_node_container.functions.alive() \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': gas_estimation,
                            'gasPrice': int(gas_price)})
                if name in 'acceptAssignment':
                    raw_transaction = self.worker_node_container.functions.acceptAssignment() \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': gas_estimation,
                            'gasPrice': int(gas_price)})
                if name in 'processToDataValidation':
                    raw_transaction = self.worker_node_container.functions.processToDataValidation() \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': gas_estimation,
                            'gasPrice': int(gas_price)})
                if name in 'reportInvalidData':
                    raw_transaction = self.worker_node_container.functions.reportInvalidData() \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': gas_estimation,
                            'gasPrice': int(gas_price)})
                if name in 'acceptValidData':
                    raw_transaction = self.worker_node_container.functions.acceptValidData() \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': gas_estimation,
                            'gasPrice': int(gas_price)})
                if name in 'processToCognition':
                    raw_transaction = self.worker_node_container.functions.processToCognition() \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': gas_estimation,
                            'gasPrice': int(gas_price)})
                if name in 'provideResults':
                    raw_transaction = self.worker_node_container.functions.provideResults(str.encode(result_file[0])) \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': int(gas_estimation),
                            'gasPrice': int(gas_price)})
                if name in 'checkJobQueue':
                    raw_transaction = self.pandora_container.functions.checkJobQueue() \
                        .buildTransaction({
                            'from': checksum_worker_node_account,
                            'nonce': nonce,
                            'gas': int(gas_estimation),
                            'gasPrice': int(gas_price)})

                if raw_transaction is not None:
                    signed_transaction = self.worker_node_container.web3.eth.account.signTransaction(raw_transaction,
                                                                                                     private_key)
                    tx_hash = self.worker_node_container.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
                    self.logger.info('TX_HASH : ' + tx_hash.hex())
                    self.logger.info('Waiting for receipt...')
                    transaction_receipt = self.worker_node_container.web3.eth.waitForTransactionReceipt(tx_hash,
                                                                                                        timeout=300)
                    if transaction_receipt:
                        self.logger.info('TX_RECEIPT : ' + str(transaction_receipt))
                        self.logger.info('TRANSACTION_STATUS = ' + str(transaction_receipt['status']))
                        tx_status = transaction_receipt['status']
                        if name in 'provideResults':
                            self.state_transact('checkJobQueue')
                    time.sleep(5)  # wait some time after transaction (nonce refreshing on node)
                else:
                    self.logger.info('Unknown state transaction. Skip.')
                    tx_status = 1  # for unknown state transaction reason
            except Exception as ex:
                self.logger.error("Error executing %s transaction: %s", name, type(ex))
                self.logger.error(ex.args)
                time.sleep(5)
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
        self.processors = {}  # re init processors list (while node working on one job per iteration)
        self.job_container = None  # clean up job container for prevent calculating same data on next job
        self.job_state_thread_flag = False  # finalize job event listener loop
        self.job_state_event_thread = None
        self.logger.info('Job container cleaned up')
        self.transact_progress(100, True)
        self.state_transact('provideResults', results_file)

    def processor_computing_failure(self, processor_id: Union[str, None]):
        self.logger.critical("Can't complete computing, exiting in order to reboot and try to repeat the work.")
        self.restart_pynode()

# ----------------------------------------------------------------------------------------------------------
# Kernel progress delegate methods
# ----------------------------------------------------------------------------------------------------------
    def on_train_begin(self, logs):
        print('CALL : ON_TRAIN_BEGIN')
        self.start_training_time = time.time()
        self.send_progress = False
        self.sends_count = 1
        return

    def on_train_end(self, logs):
        print('CALL : ON_TRAIN_END')
        self.finish_training_time = time.time()
        self.logger.info('Total training time : ' + str(self.finish_training_time - self.start_training_time))
        self.send_progress = False
        self.sends_count = 1
        return

    def on_epoch_begin(self, epoch, epochs, logs):
        self.current_epoch = epoch
        self.start_epoch_time = time.time()
        return

    def on_epoch_end(self, epoch, epochs, logs):
        self.finish_epoch_time = time.time()
        # process calculation on first epoch finish
        if self.current_epoch == 0:
            self.logger.info('')
            self.logger.info('---------------------------------------------------------------------')
            self.logger.info('Epoch ' + str(epoch) + ' of ' + str(epochs))
            self.time_per_epoch = self.finish_epoch_time - self.start_epoch_time
            self.logger.info('Time per epoch : ' + str(self.time_per_epoch))
            total_time = self.time_per_epoch * epochs
            self.logger.info('Total training time : ' + str(total_time))
            if total_time > self.send_progress_interval:
                self.send_progress = True
            self.logger.info('Send progress strategy enabled : ' + str(self.send_progress))
            time.sleep(5)
            return
        if self.send_progress:
            current_percent = int(100/epochs * epoch)
            self.logger.info('Current percent : ' + str(current_percent))
            if time.time() >= self.start_training_time + (self.send_progress_interval * self.sends_count):
                self.logger.info("transact presents : " + str(current_percent) + '%')
                Thread(target=self.transact_progress(current_percent, False), args=(), daemon=True).start()
                self.sends_count += 1
                self.logger.info('CURRENT MODIFIER VALUE : ' + str(self.sends_count))
        return

    def transact_progress(self, percents, wait_receipt):
        self.logger.info("Transact progress to worker node")
        private_key = self.key_tool.obtain_key(self.manager.vault_key).split("_", 1)[1]
        tx_status = 0
        while tx_status == 0:
            try:
                nonce = self.worker_node_container.web3.eth.getTransactionCount(self.manager.eth_worker_node_account,
                                                                                "pending")
                self.logger.info('Calculate gas estimation...')
                gas_estimation = self.worker_node_container.web3.eth.generateGasPrice()
                gas_price = self.worker_node_container.web3.eth.gasPrice
                self.logger.info('Gas estimated : ' + str(gas_estimation))
                raw_transaction = self.worker_node_container.functions.reportProgress(percents) \
                    .buildTransaction({'from': self.manager.eth_worker_node_account,
                                       'nonce': nonce,
                                       'gas': int(gas_estimation + gas_estimation/2),
                                       'gasPrice': int(gas_price)})
                signed_transaction = self.worker_node_container.web3.eth.account.signTransaction(raw_transaction,
                                                                                                 private_key)
                tx_hash = self.worker_node_container.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
                self.logger.info('TX_HASH : ' + tx_hash.hex())
                if wait_receipt:
                    self.logger.info('Waiting for receipt...')
                    transaction_receipt = self.worker_node_container.web3.eth.waitForTransactionReceipt(tx_hash,
                                                                                                        timeout=300)
                    if transaction_receipt:
                        self.logger.info('TX_RECEIPT : ' + str(transaction_receipt))
                        self.logger.info('TRANSACTION_STATUS = ' + str(transaction_receipt['status']))
                        tx_status = transaction_receipt['status']
                        time.sleep(2)  # wait some time after transaction (nonce refreshing on node)
                    else:
                        self.logger.info('Unknown state transaction. Skip.')
                        tx_status = 1  # for unknown state transaction reason
                        return
                else:
                    tx_status = 1
            except Exception as ex:
                self.logger.error("Error executing progress transaction: %s", type(ex))
                self.logger.error(ex.args)
                time.sleep(5)
        return

# ----------------------------------------------------------------------------------------------------------
# System methods
# ----------------------------------------------------------------------------------------------------------
    def restart_pynode(self):
        """ Restart pynode due keras or tensorflow exception """
        os.chdir(self.manager.primary_wd)
        script = os.path.join(self.manager.primary_wd, 'pynode.py')
        subprocess.Popen(
            [sys.executable, script, '-p' + self.manager.vault_key + ''])
        sys.exit()
