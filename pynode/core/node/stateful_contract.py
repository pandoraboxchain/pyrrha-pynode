from core.manager import Manager
from core.patterns.state_machine import StateMachine, StateTable


class StatefulContract(StateMachine):

    DESTROYED = 0xFF
    UNINITIALIZED = 0x00

    def __init__(self, contract_container, table: StateTable, *args, **kwargs):
        StateMachine.__init__(self, table=table)
        self.contract_container = contract_container

    def process_state(self):
        state = 0
        try:
            state = self.contract_container.call().currentState()
        except Exception as ex:
            self.logger.info('Exception on process worker state.')
            self.logger.info(ex.args)
        Manager.get_instance().set_job_contract_state(self.state_table[state].name)
        self.logger.info("Contract %s initial state is %s", self.__class__.__name__, self.state_table[state].name)
        self.state = state
        return state


