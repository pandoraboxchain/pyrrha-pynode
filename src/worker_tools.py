import logging
import time

from eth.eth_connector import EthConnector
from patterns.pynode_logger import LogSocketHandler
from manager import Manager
from configparser import ConfigParser
"""
Class tool for ask Pandora to create new Worker contract and obtain 
 new created worker contract address
"""


class WorkerMaker:

    obtaining_flag = False

    def __init__(self, eth_server: str, abi_path: str, pandora: str):
        # Initializing logger object
        self.logger = logging.getLogger("WorkerTools")
        self.logger.addHandler(LogSocketHandler.get_instance())

        self.manager = Manager.get_instance()
        self.config = ConfigParser()

        # Saving config
        self.eth_server = eth_server
        self.abi_path = abi_path

        EthConnector.server = self.eth_server
        EthConnector.logger = self.logger

        # init pandora contract
        self.pandora = EthConnector(address=pandora,
                                    contract=self.manager.eth_pandora_contract)

    def connect(self) -> bool:
        try:
            result = EthConnector.connect()
            result &= self.pandora.init_contract() if result else False
        except Exception as ex:
            self.logger.error("Exception initializing contracts: %s", type(ex))
            self.logger.error(ex.args)
            return False
        if result is not True:
            self.logger.error("Unable to start worker maker, exiting")
            return False
        # bind event on worker node contract creation
        self.pandora.bind_event('WorkerNodeCreated', self.on_worker_node_created)
        return True

    def create_worker(self, address: str):
        self.logger.info("Obtaining worker contract address")
        try:
            is_address = self.pandora.web3.isAddress(address)
            if is_address is False:
                self.logger.info('Invalid address for worker creation, exiting')
                return
            tx_result_hash = self.pandora.transact('createWorkerNode', lambda tx: tx.createWorkerNode(), address)
            self.pandora.get_transaction_receipt(tx_result_hash)
            while self.obtaining_flag is False:
                # await for async callback
                time.sleep(3)
        except Exception as ex:
            self.logger.error("Exception initializing contracts: %s", type(ex))
            self.logger.error(ex.args)

    def on_worker_node_created(self, event: dict):
        try:
            address = event['args']['workerNode']
            self.logger.info("Node creation success address : %s", address)
            self.logger.info("Storing worker address to config file")
            self.config.read(self.manager.pynode_config_file_path)

            cfg_file = open(self.manager.pynode_config_file_path, 'w')
            self.config.set('Contracts', 'worker_node', str(address))
            self.config.write(cfg_file)
            cfg_file.close()
        except Exception as ex:
            self.logger.error("Exception retrieving worker contract address")
            self.logger.error(ex.args)
        self.logger.info("Address is stored in default config file on Ethereum section")
        self.logger.info("Please save the address in order to avoid losing it")
        self.obtaining_flag = True



