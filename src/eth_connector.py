from web3 import Web3, KeepAliveRPCProvider


DEFAULT_CONTRACT_ADDR = ''

class EthConnector:

    def __init__(self, host: str='localhost', port: str='8545', contract_addr: str=DEFAULT_CONTRACT_ADDR):
        self.web3 = Web3(KeepAliveRPCProvider(host=host, port=port))
        self.root_contract = self.web3.eth.Eth.contract(address=contract_addr)
