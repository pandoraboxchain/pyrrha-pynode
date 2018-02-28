from eth.eth_connector import EthConnector
from manager import Manager
from patterns.state_machine import *


class StatefulContract(EthConnector, StateMachine):

    DESTROYED = 0xFF
    UNINITIALIZED = 0x00

    def __init__(self, table: StateTable, *args, **kwargs):
        EthConnector.__init__(self, *args, **kwargs)
        StateMachine.__init__(self, table=table)

    def bootstrap(self) -> bool:
        self.__process_state()
        return self.__bind_events()

    def __process_state(self):
        state = self.contract.call().currentState()
        # set job contract initial state
        Manager.get_instance().set_job_contract_state(self.state_table[state].name)
        self.logger.info("Contract %s initial state is %s", self.__class__.__name__, self.state_table[state].name)
        self.state = state

    def __bind_events(self) -> bool:
        self.logger.info("Binding state changing events")
        try:
            self.bind_event('StateChanged', self.__on_state_changed)
        except Exception as ex:
            self.logger.error("Error binging events: %s", type(ex))
            self.logger.error(ex.args)
            return False
        return True

    def __on_state_changed(self, event: dict):
        state_old = event['args']['oldState']
        state_new = event['args']['newState']
        # set job contract state change
        if self.__class__.__name__ == 'WorkerNode':
            Manager.get_instance().set_worker_contract_state(self.state_table[state_new].name)
        if self.__class__.__name__ == 'CognitiveJob':
            Manager.get_instance().set_job_contract_state(self.state_table[state_new].name)
        # print log and instantiate new state
        self.logger.info("Contract %s changed its state from %s to %s",
                         self.__class__.__name__,
                         self.state_table[state_old].name,
                         self.state_table[state_new].name)
        self.state = state_new
