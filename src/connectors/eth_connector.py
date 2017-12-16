import json
import logging
from typing import Callable
from patterns.decorators import *
from patterns.exceptions import *
from os import path
from web3 import Web3, HTTPProvider


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

    def __init__(self, host: str, port: int, address: str, abi_path: str, abi_file: str):
        # Initializing logger object
        self.logger = logging.getLogger("EthConnector")

        # Saving config
        self.host = host
        self.port = port
        self.address = address
        self.abi_path = abi_path
        self.abi_file = abi_file

        # Initializing empty config
        self.web3 = None
        self.contract = None
        self.event_filter = None

    @run_once
    def connect(self) -> bool:
        self.logger.debug('Connecting to Ethereum node on %s:%d...', self.host, self.port)
        try:
            self.web3 = Web3(HTTPProvider('%s:%d' % (self.host, self.port)))
            info = self.web3.eth.syncing
        except Exception as ex:
            self.logger.error('Error connecting Ethereum node: %s', type(ex))
            self.logger.error(ex.args)
            return False

        if info is not False:
            self.logger.error('Ethereum node is not in synch')
            return False

        self.logger.debug('Ethereum node connected successfully. Here is an info about it:')
        self.logger.debug(info)
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
            self.contract.call().owner()
        except Exception as ex:
            self.logger.error('Wrong contract ABI, got exception %s', type(ex))
            self.logger.error(ex.args)
            return False

        return True

    @run_once
    def bind_events(self, event: str, callback: Callable[[object], None]):
        if self.contract is None:
            raise NotInitialized()
        self.event_filter = self.contract.on(event)
        self.event_filter.start()
        self.event_filter.watch(callback)

    def contract_at(self, address: str, abi_file: str):
        if self.web3 is None:
            raise NotInitialized()

        self.logger.debug('Reading contract ABI %s...', abi_file)
        try:
            abi = read_abi(self.abi_path, abi_file)
        except Exception as ex:
            self.logger.error('Error reading contract ABI file: %s', type(ex))
            self.logger.error(ex.args)
            return None

        self.logger.debug('Getting contract %s...', address)
        try:
            contract = self.web3.eth.contract(address=address, abi=abi)
        except Exception as ex:
            self.logger.error('Error getting contract: %s', type(ex))
            self.logger.error(ex.args)
            return None
        self.logger.debug('Contract ABI instantiated')

        return contract
