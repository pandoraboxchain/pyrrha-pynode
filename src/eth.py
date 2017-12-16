import json
import logging
from os import path
from threading import *
from collections import namedtuple
from web3 import Web3, KeepAliveRPCProvider


EthConfig = namedtuple('EthConfig', 'server port contract abi hooks')


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


class Eth(Thread):
    """
    Class implementing connection and interfaces to Ethereum network
    """

    EventFilters = namedtuple('EventFilters', 'job_created worker_state')

    EVENT_CREATE_JOB = 'CognitiveJobCreated'

    ABI_PANDORA = 'Pandora'
    ABI_PANDORA_HOOKS = 'PandoraHooks'
    ABI_WORKER_NODE = 'WorkerNode'
    ABI_COGNITIVE_JOB = 'CognitiveJob'
    ABI_KERNEL = 'Kernel'
    ABI_DATASET = 'Dataset'

    def __init__(self, config: EthConfig):
        """
        Constructor taking a single argument. Constructor does not connect to Ethereum network or performs any tasks
        that can fail. Instead, all the actual job is done by the `run` function that should be called after the class
        creation.

        :param config: Named configuration tuple of type `EthConfig` that should be imported from this file.
        Contains configuration for connecting Ethereum node (`server`, `port`), address of the main Pandora contract,
        `abi` as a path to directory with contract ABI files (are submodule to this project) and
        a flag `hooks` indicating whether the main Pandora contract or debug PandoraHooks contract should be used.
        """

        # Initializing logger object
        self.logger = logging.getLogger("eth")

        # Saving config
        self.config = config

        # Initializing empty config
        self.web3 = None
        self.pandora_contract = None
        self.abi = {}
        self.event_filters = self.EventFilters(job_created=None, worker_state=None)

        # Initializing thread superclass
        super().__init__()

    def run(self) -> bool:
        """
        Starts connections to Ethereum network, reads ABI files, initializes contracts, launches thread and bind
        Ethereum events

        :return: Success or failure (True/False)
        """

        if not (self.__connect_ethereum()
           and self.__load_abi()
           and self.__connect_pandora()):
            return False

        super().run()

        ef = self.pandora_contract.on(self.EVENT_CREATE_JOB)
        ef.start()
        ef.watch(self.__on_cognitive_job_created)
        ef.join()

        self.event_filters.job_created = ef

        return True

    ##
    # Private initialization methods
    ##

    def __connect_ethereum(self) -> bool:
        self.logger.debug('Connecting to Ethereum node on %s:%d...', self.config.server, self.config.port)
        try:
            self.web3 = Web3(KeepAliveRPCProvider(host=self.config.server, port=self.config.port))
        except Exception as ex:
            self.logger.error('Error connecting Ethereum node: %s', type(ex))
            self.logger.error(ex.args)
            return False
        self.logger.debug('Ethereum node connected successfully')
        return True

    def __load_abi(self) -> bool:
        abi_path = self.config.abi

        self.abi = {
            self.ABI_KERNEL: read_abi(abi_path, self.ABI_KERNEL),
            self.ABI_DATASET: read_abi(abi_path, self.ABI_DATASET),
            self.ABI_COGNITIVE_JOB: read_abi(abi_path, self.ABI_COGNITIVE_JOB)
        }
        return True

    def __connect_pandora(self) -> bool:
        abi_file = self.ABI_PANDORA_HOOKS if self.config.hooks is True else self.ABI_PANDORA
        abi = read_abi(self.config.abi, abi_file)

        self.logger.debug('Getting root contract %s...', self.config.contract)
        try:
            self.pandora_contract = self.web3.eth.contract(address=self.config.contract, abi=abi)
        except Exception as ex:
            self.logger.error('Error connecting Ethereum node: %s', type(ex))
            self.logger.error(ex.args)
            return False
        self.logger.debug('Root contract ABI instantiated')
        return True

    ##
    # Ethereum contracts event listeners
    ##

    def __on_cognitive_job_created(self, event: dict):
        address = event['args']['cognitiveJob']
        self.logger.debug('=> Got new cognitive job contract %s', address)
        contract = self.web3.eth.contract(address=address, abi=self.abi[self.ABI_COGNITIVE_JOB])
        # event = CognitiveJobCreated(contract, address)
        # self.trigger(event)
