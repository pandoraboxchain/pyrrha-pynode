from .node_actions import *


class WorkerNode(NodeActions):
    # States

    OFFLINE = 1
    IDLE = 2
    ASSIGNED = 3
    READY_FOR_DATA_VALIDATION = 4
    VALIDATING_DATA = 5
    READY_FOR_COMPUTING = 6
    COMPUTING = 7
    INSUFFICIENT_STAKE = 8
    UNDER_PENALTY = 9

    # State table

    def __init__(self, *args, **kwargs):
        table = {
            self.UNINITIALIZED: StateTableEntry('Uninitialized',
                                                transits_to=[self.IDLE, self.OFFLINE, self.INSUFFICIENT_STAKE],
                                                on_enter=self.state_uninitialized_on_enter,
                                                on_exit=self.state_uninitialized_on_exit),
            self.DESTROYED: StateTableEntry('Destroyed',
                                            transits_to=[],
                                            on_enter=self.state_destroyed_on_enter,
                                            on_exit=self.state_destroyed_on_exit),

            self.OFFLINE: StateTableEntry('Offline',
                                          transits_to=[self.IDLE],
                                          on_enter=self.state_offline_on_enter,
                                          on_exit=self.state_offline_on_exit),
            self.IDLE: StateTableEntry('Idle',
                                       transits_to=[self.OFFLINE, self.ASSIGNED,
                                                    self.UNDER_PENALTY, self.DESTROYED],
                                       on_enter=self.state_idle_on_enter,
                                       on_exit=self.state_idle_on_exit),
            self.ASSIGNED: StateTableEntry('Assigned',
                                           transits_to=[self.OFFLINE, self.READY_FOR_DATA_VALIDATION,
                                                        self.UNDER_PENALTY],
                                           on_enter=self.state_assigned_on_enter,
                                           on_exit=self.state_assigned_on_exit),
            self.READY_FOR_DATA_VALIDATION: StateTableEntry('ReadyForDataValidation',
                                                            transits_to=[self.OFFLINE, self.VALIDATING_DATA, self.IDLE,
                                                                         self.UNDER_PENALTY],
                                                            on_enter=self.state_rfdv_on_enter,
                                                            on_exit=self.state_rfdv_on_exit),
            self.VALIDATING_DATA: StateTableEntry('ValidatingData',
                                                  transits_to=[self.OFFLINE, self.IDLE, self.READY_FOR_COMPUTING,
                                                               self.UNDER_PENALTY],
                                                  on_enter=self.state_validating_data_on_enter,
                                                  on_exit=self.state_validating_data_on_exit),
            self.READY_FOR_COMPUTING: StateTableEntry('ReadyForComputing',
                                                      transits_to=[self.OFFLINE, self.IDLE, self.COMPUTING,
                                                                   self.UNDER_PENALTY],
                                                      on_enter=self.state_ready_for_computing_on_enter,
                                                      on_exit=self.state_ready_for_computing_on_exit),
            self.COMPUTING: StateTableEntry('Computing',
                                            transits_to=[self.OFFLINE, self.IDLE, self.UNDER_PENALTY],
                                            on_enter=self.state_computing_on_enter,
                                            on_exit=self.state_computing_on_exit),
            self.INSUFFICIENT_STAKE: StateTableEntry('InsufficientStake',
                                                     transits_to=[self.OFFLINE, self.IDLE, self.DESTROYED],
                                                     on_enter=self.state_insufficient_stake_on_enter,
                                                     on_exit=self.state_insufficient_stake_on_exit),
            self.UNDER_PENALTY: StateTableEntry('UnderPenalty',
                                                transits_to=[self.OFFLINE, self.IDLE, self.INSUFFICIENT_STAKE],
                                                on_enter=self.state_under_penalty_on_enter,
                                                on_exit=self.state_under_penalty_on_exit),
        }
        super().__init__(table=table, *args, **kwargs)

    def state_uninitialized_on_enter(self, from_state: int):
        pass

    def state_uninitialized_on_exit(self, from_state: int):
        pass

    def state_destroyed_on_enter(self, from_state: int):
        pass

    def state_destroyed_on_exit(self, from_state: int):
        pass

    def state_offline_on_enter(self, from_state: int):
        self.transact_alive()

    def state_offline_on_exit(self, from_state: int):
        pass

    def state_idle_on_enter(self, from_state: int):
        pass

    def state_idle_on_exit(self, from_state: int):
        pass

    def state_assigned_on_enter(self, from_state: int):
        self.transact_accept_assignment()

    def state_assigned_on_exit(self, from_state: int):
        pass

    def state_rfdv_on_enter(self, from_state: int):
        self.transact_process_to_data_validation()

    def state_rfdv_on_exit(self, from_state: int):
        pass

    def state_validating_data_on_enter(self, from_state: int):
        self.transact_accept_valid_data()

    def state_validating_data_on_exit(self, from_state: int):
        pass

    def state_ready_for_computing_on_enter(self, from_state: int):
        self.transact_process_to_cognition()

    def state_ready_for_computing_on_exit(self, from_state: int):
        pass

    def state_computing_on_enter(self, from_state: int):
        self.transact_provide_results('')

    def state_computing_on_exit(self, from_state: int):
        pass

    def state_insufficient_stake_on_enter(self, from_state: int):
        pass

    def state_insufficient_stake_on_exit(self, from_state: int):
        pass

    def state_under_penalty_on_enter(self, from_state: int):
        pass

    def state_under_penalty_on_exit(self, from_state: int):
        pass
