from pynode.integration.eth_service import EthAbstract
from typing import Callable


class EthConnectorDummy(EthAbstract):

    def init_contract(self, server_address: str, contract_address: str, contract_abi: str):
        pass

    def bind_event(self, contract, event: str, callback: Callable[[object], None]):
        pass

    def get_accounts_list(self):
        pass

    def get_transaction_receipt(self, tx_hash: str):
        pass

    def transact(self, cb: Callable):
        pass


