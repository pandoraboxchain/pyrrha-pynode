from .singleton import Singleton

from web3 import Web3, KeepAliveRPCProvider


class EthConnector(Singleton):
    __web3 = Web3(KeepAliveRPCProvider(host='localhost', port='8545'))
    __contract_address = ""

    def __init__(self):
        self.contract = EthConnector.__web3.eth.Eth.contract(address=EthConnector.__contract_address)
        pass
