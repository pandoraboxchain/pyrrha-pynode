from typing import Callable
from integration.eth_service import EthAbstract
from web3 import Web3, HTTPProvider
from core.patterns.exceptions import EthConnectionException, EthIsNotInSyncException, WrongContractAddressOrABI


class EthConnector(EthAbstract):

    def init_contract(self, server_address: str, contract_address: str, contract_abi: str):
        EthConnector.web3 = Web3(HTTPProvider(server_address))
        try:
            info = EthConnector.web3.eth.syncing
        except Exception as ex:
            raise EthConnectionException('Error connecting Ethereum node', ex)

        if info is not False:
            raise EthIsNotInSyncException('Ethereum node is not in synch', info)
        contract = EthConnector.web3.eth.contract(address=contract_address, abi=contract_abi)
        return contract

    def bind_event(self, contract, event: str, callback: Callable[[object], None]):
        event_filter = None
        try:
            event_filter = contract.on(event)
            event_filter.start()
            event_filter.watch(callback)
        except Exception as ex:
            print('Except event filter listener instantiation : ' + str(ex.args[0]))
        return event_filter

    def get_accounts_list(self):
        return EthConnector.web3.eth.accounts

    def get_transaction_receipt(self, tx_hash: str):
        return EthConnector.web3.eth.getTransactionReceipt(tx_hash)

    def transact(self, contract, cb: Callable):
        try:
            return contract.transact(cb)
        except Exception as ex:
            print('Except transact : ' + ex.args)
