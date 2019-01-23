from core.manager import Manager
from core.patterns.state_machine import StateMachine, StateTable


class JobStatefulContract(StateMachine):
    DESTROYED = 0xFF
    UNINITIALIZED = 0x00

    def __init__(self, job_controller_container, table: StateTable, *args, **kwargs):
        StateMachine.__init__(self, table=table)
        self.job_controller_container = job_controller_container

    def process_state(self, job_id_hex):
        state = 0
        try:
            state = self.job_controller_container.call().getCognitiveJobDetails(job_id_hex)[7]
        except Exception as ex:
            self.logger.info('Exception on process job state.')
            self.logger.info(ex.args)
        Manager.get_instance().set_job_contract_state(self.state_table[state].name)
        self.logger.info("Contract %s initial state is %s", self.__class__.__name__, self.state_table[state].name)
        self.state = state
        return state