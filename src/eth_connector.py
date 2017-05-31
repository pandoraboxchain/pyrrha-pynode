from collections import namedtuple
from web3 import Web3, KeepAliveRPCProvider


EthConfig = namedtuple('EthConfig', 'server port contract')

DEFAULT_CONTRACT_ADDR = ''


class EthConnector:

    def __init__(self, config: EthConfig):
        self.config = config
        self.web3 = Web3(KeepAliveRPCProvider(host=self.config.server, port=self.config.port))
        self.root_contract = self.web3.eth.contract(address=self.config.contract)
