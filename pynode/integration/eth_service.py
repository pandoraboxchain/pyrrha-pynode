from abc import ABCMeta, abstractmethod
from typing import Callable


class EthAbstract(metaclass=ABCMeta):

    @abstractmethod
    def init_contract(self, server_address: str, contract_address: str, contract_abi: str):
        pass

    @abstractmethod
    def bind_event(self, contract, event: str, callback: Callable[[object], None]):
        pass

    @abstractmethod
    def get_accounts_list(self):
        pass

    @abstractmethod
    def get_transaction_receipt(self, tx_hash: str):
        pass

    @abstractmethod
    def transact(self, cb: Callable):
        pass


class EthService(EthAbstract):

    def __init__(self, strategic: EthAbstract):
        self.strategy = strategic

    def init_contract(self, server_address: str, contract_address: str, contract_abi: str):
        return self.strategy.init_contract(server_address=server_address,
                                           contract_address=contract_address,
                                           contract_abi=contract_abi)

    def bind_event(self, contract, event: str, callback: Callable[[object], None]):
        return self.strategy.bind_event(contract=contract,
                                        event=event,
                                        callback=callback)

    def get_accounts_list(self):
        return self.strategy.get_accounts_list()

    def get_transaction_receipt(self, tx_hash: str):
        return self.strategy.get_transaction_receipt(tx_hash)

    def transact(self, cb: Callable):
        return self.strategy.transact(cb)

