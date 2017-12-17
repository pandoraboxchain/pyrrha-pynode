from eth.eth_connector import EthConnector
from patterns.state_machine import *


class StatefulContract(EthConnector, StateMachine):

    DESTROYED = 0xFF
    UNINITIALIZED = 0x00

    def __init__(self, table: StateTable, *args, **kwargs):
        EthConnector.__init__(self, *args, **kwargs)
        StateMachine.__init__(self, table=table)

    def bootstrap(self) -> bool:
        self.connect()
        self.init_contract()
        self.__process_state()
        self.bind_event('StateChanged', self.__on_state_changed)
        self.event_filter.join()
        return True

    def __process_state(self):
        state = self.contract.call().currentState()
        self.logger.debug("Contract %s initial state is %s", self.abi_file, state)
        self.state = state

    def __on_state_changed(self, event: dict):
        state_old = event['args']['oldState']
        state_new = event['args']['newDtate']
        self.logger.debug("Contract %s changed its state from %s to %s", self.abi_file, state_old, state_new)
        self.state = state_new
