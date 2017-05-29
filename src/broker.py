from .singleton import Singleton

from .nn_loader import NNLoader
from .ipfs_connector import IPFSConnector
from .eth_connector import EthConnector
from .mn_connector import MNConnector
from .processor import Processor
from .verificator import Verificator


class Broker (Singleton):

    __loader = None
    __ipfs = None
    __eth = None
    __mn = None
    __processor = None
    __verificator = None

    def __init__(self):
        # Set up IPFS link
        self.__ipfs = IPFSConnector()
        # Set up Ethereum node link
        self.__eth = EthConnector()
        # Set up masternode connections
        self.__mn = MNConnector()

        self.__loader = NNLoader()
        self.__processor = Processor()
        self.__verificator = Verificator()

    def run(self):
        self.__mn.serve()
