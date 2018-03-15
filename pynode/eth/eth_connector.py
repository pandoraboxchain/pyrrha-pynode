import logging

from manager import Manager
from typing import Callable
from patterns.decorators import run_once
from web3 import Web3, HTTPProvider
from patterns.pynode_logger import LogSocketHandler
from patterns.exceptions import EthConnectionException, \
                                EthIsNotInSyncException, \
                                CriticalTransactionError, \
                                NotInitialized, \
                                WrongContractAddressOrABI


class EthConnector:
    """
    Base class implementing Ethereum network connectivity.
    Inherited classes will have dedicated connection to Ethereum node (one per class instance) which is the
    design enabling multi-threaded workflows without bottle necks and inter-thread locks.

    Class takes some contract as its main contract (see constructor arguments) and binds event listeners to it,
    exposing its Web3 contract interface via `EthConnector.contract` property.

    Class also allows accessing other contracts, simplifying Web3 API usage to instantiate them.
    """
    logger = None
    web3 = None
    account = None
    server = None
    mode = None

    def __init__(self, address: str, contract):
        # Initializing logger object
        self.logger = logging.getLogger("EthConnector")
        self.logger.addHandler(LogSocketHandler.get_instance())
        self.mode = Manager.get_instance().launch_mode

        # Saving config
        self.address = address
        self.abi_file = contract

        # Initializing empty config
        self.contract = None
        self.event_filter = None
        self.owner = None

    @staticmethod
    def connect() -> bool:
        mode = Manager.get_instance().launch_mode
        if EthConnector.web3 is not None and not mode == 1:
            return True

        EthConnector.logger.info('Connecting Ethereum node on %s...', EthConnector.server)
        try:
            EthConnector.web3 = Web3(HTTPProvider(EthConnector.server))
            info = EthConnector.web3.eth.syncing
        except Exception as ex:
            EthConnector.logger.error('Error connecting Ethereum node: %s', type(ex))
            EthConnector.logger.error(ex.args)
            if mode == 1:
                raise EthConnectionException('Error connecting Ethereum node', ex)
            return False

        if info is not False:
            EthConnector.logger.error('Ethereum node is not in synch')
            if mode == 1:
                raise EthIsNotInSyncException('Ethereum node is not in synch', info)
            return False
        Manager.get_instance().set_state('Online')
        EthConnector.logger.info('Ethereum node connected successfully')
        return True

    @run_once
    def init_contract(self) -> bool:
        if self.web3 is None:
            raise NotInitialized("Web 3 is not initialized, unable to connect")
        try:
            self.contract = self.contract_at(self.address)
            self.owner = self.contract.call().owner()
        except Exception as ex:
            self.logger.error('Wrong contract address or ABI, got exception %s', type(ex))
            self.logger.error(ex.args)
            if self.mode == 1:
                raise WrongContractAddressOrABI('Wrong contract address or ABI', ex)
            return False

        return True

    @run_once
    def bind_event(self, event: str, callback: Callable[[object], None]):
        if self.contract is None:
            raise NotInitialized()
        self.event_filter = self.contract.on(event)
        self.event_filter.start()
        self.event_filter.watch(callback)

    def contract_at(self, address: str):
        if self.web3 is None:
            raise NotInitialized()
        try:
            contract = self.web3.eth.contract(address=address, abi=self.abi_file)
        except Exception as ex:
            self.logger.error('Error getting contract: %s', type(ex))
            self.logger.error(ex.args)
            return None
        Manager.get_instance().set_worker_contract_state('Initialized')
        self.logger.info('Connector %s ABI instantiated', address)

        return contract

    def get_transaction_receipt(self, tx_hash: str):
        try:
            return self.web3.eth.getTransactionReceipt(tx_hash)
        except Exception as ex:
            self.logger.error('Error reading transaction receipt')
            self.logger.error(ex.args)

    def transact(self, name: str, cb: Callable, *args):
        try:
            # in current time on worker node creation we need possibility to change
            # customer address for witch new Worker Node contract will be created
            if args:
                tx = self.contract.transact({'from': args[0]})
            else:
                tx = self.contract.transact({'from': self.web3.eth.accounts[0]})
            return cb(tx)
        except Exception as ex:
            self.logger.error("Error executing %s transaction: %s", name, type(ex))
            self.logger.error(ex.args)
            raise CriticalTransactionError(name)
