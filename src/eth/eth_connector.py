import json
import logging
from typing import Callable
from patterns.decorators import *
from patterns.exceptions import *
from os import path
from web3 import Web3, HTTPProvider


class CriticalTransactionError(Exception):
    pass


def read_abi(abi_path: str, file: str) -> str:
    """
    Loads ABI from a compiled file

    :param abi_path: path to directory (relative to the current file) that contains ABI files
    :param file: name of the ABI file (without extension, it should be .json)
    :return: returns read ABI dictionary object suitable for using in Web3
    """

    here = path.abspath(path.dirname(__file__))
    file = "%s.json" % file
    with open(path.join(here, abi_path, file), encoding='utf-8') as f:
        artifact = json.load(f)
    return artifact['abi']


class EthConnector:
    """
    Base class implementing Ethereum network connectivity.
    Inherited classes will have dedicated connection to Ethereum node (one per class instance) which is the
    design enabling multi-threaded workflows without bottle necks and inter-thread locks.

    Class takes some contract as its main contract (see constructor arguments) and binds event listeners to it,
    exposing its Web3 contract interface via `EthConnector.contract` property.

    Class also allows accessing other contracts, simplifying Web3 API usage to instantiate them.
    """

    read_abi = staticmethod(read_abi)

    web3 = None
    account = None
    server = None

    def __init__(self, address: str, abi_path: str, abi_file: str):
        # Initializing logger object
        self.logger = logging.getLogger("EthConnector")

        # Saving config
        self.address = address
        self.abi_path = abi_path
        self.abi_file = abi_file

        # Initializing empty config
        self.contract = None
        self.event_filter = None
        self.owner = None

    @staticmethod
    def connect(private_key: str) -> bool:
        if EthConnector.web3 is not None:
            return True

        logging.info('Connecting Ethereum node on %s...', EthConnector.server)
        try:
            EthConnector.web3 = Web3(HTTPProvider(EthConnector.server))
            info = EthConnector.web3.eth.syncing
        except Exception as ex:
            logging.error('Error connecting Ethereum node: %s', type(ex))
            logging.error(ex.args)
            return False

        if info is not False:
            logging.error('Ethereum node is not in synch')
            return False

        try:
            pass
            # EthConnector.account = EthConnector.web3.eth.account.privateKeyToAccount(private_key)
        except Exception as ex:
            logging.error('Error initializing Ethereum account: %s', type(ex))
            logging.error(ex.args)
            EthConnector.web3 = None
            return False

        logging.info('Ethereum node connected successfully')
        return True

    @run_once
    def init_contract(self) -> bool:
        if self.web3 is None:
            raise NotInitialized()

        self.contract = self.contract_at(self.address, self.abi_file)
        if self.contract is False:
            return False

        # Calling getter method to check whether contract was initiated with a proper address
        # (corresponding to the given ABI)
        try:
            self.owner = self.contract.call().owner()
        except Exception as ex:
            self.logger.error('Wrong contract address or ABI, got exception %s', type(ex))
            self.logger.error(ex.args)
            return False

        return True

    @run_once
    def bind_event(self, event: str, callback: Callable[[object], None]):
        if self.contract is None:
            raise NotInitialized()
        self.event_filter = self.contract.on(event)
        self.event_filter.start()
        self.event_filter.watch(callback)

    def contract_at(self, address: str, abi_file: str):
        if self.web3 is None:
            raise NotInitialized()

        self.logger.info('Reading contract ABI %s...', abi_file)
        try:
            abi = read_abi(self.abi_path, abi_file)
        except Exception as ex:
            self.logger.error('Error reading contract ABI file: %s', type(ex))
            self.logger.error(ex.args)
            return None

        self.logger.info('Getting contract %s...', address)
        try:
            contract = self.web3.eth.contract(address=address, abi=abi)
        except Exception as ex:
            self.logger.error('Error getting contract: %s', type(ex))
            self.logger.error(ex.args)
            return None
        self.logger.info('Contract ABI instantiated')

        return contract

    def transact(self, name: str, cb: Callable):
        try:
            tx = self.contract.transact({'from': self.web3.eth.accounts[0]})
            cb(tx)
        except Exception as ex:
            self.logger.error("Error executing %s transaction: %s", name, type(ex))
            self.logger.error(ex.args)

            raise CriticalTransactionError(name)
