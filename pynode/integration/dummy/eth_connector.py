from pynode.integration.eth_service import EthAbstract
from typing import Callable
from web3 import Web3, HTTPProvider


class EthConnectorDummy(EthAbstract):

    def init_contract(self, server_address: str, contract_address: str, contract_abi: str):
        pass

    def transact(self, contract, event: str, callback: Callable[[object], None]):
        pass

    def bind_event(self, cb: Callable):
        pass

    def get_transaction_receipt(self, tx_hash: str):
        pass

    def get_accounts_list(self):
        pass
