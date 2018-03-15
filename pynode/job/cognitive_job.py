from abc import ABCMeta, abstractmethod
from patterns.state_machine import StateTableEntry
from .job_getters import JobGetters


class CognitiveJobDelegate(metaclass=ABCMeta):
    @abstractmethod
    def terminate_job(self, job):
        pass


class CognitiveJob(JobGetters):

    # States

    GATHERING_WORKERS = 1
    INSUFFICIENT_WORKERS = 2
    DATA_VALIDATION = 3
    INVALID_DATA = 4
    COGNITION = 5
    PARTIAL_RESULT = 6
    COMPLETED = 7

    def __init__(self, delegate: CognitiveJobDelegate, *args, **kwargs):

        self.delegate = delegate

        # Transition table
        table = {
            self.UNINITIALIZED: StateTableEntry('Uninitialized',
                                                transits_to=[self.GATHERING_WORKERS],
                                                on_enter=self.on_enter_state_uninitialized,
                                                on_exit=self.on_exit_state_uninitialized),
            self.DESTROYED: StateTableEntry('Destroyed',
                                            transits_to=[],
                                            on_enter=self.on_enter_state_destroyed,
                                            on_exit=self.on_exit_state_destroyed),

            self.GATHERING_WORKERS: StateTableEntry('GatheringWorkers',
                                                    transits_to=[self.INSUFFICIENT_WORKERS, self.DATA_VALIDATION],
                                                    on_enter=self.on_enter_gathering_workers,
                                                    on_exit=self.on_exit_gathering_workers),
            self.INSUFFICIENT_WORKERS: StateTableEntry('InsufficientWorkers',
                                                       transits_to=[self.DESTROYED],
                                                       on_enter=self.on_enter_insufficient_workers,
                                                       on_exit=self.on_exit_insufficient_workers),
            self.DATA_VALIDATION: StateTableEntry('DataValidation',
                                                  transits_to=[self.INVALID_DATA, self.INSUFFICIENT_WORKERS,
                                                               self.COGNITION, self.DESTROYED],
                                                  on_enter=self.on_enter_data_validation,
                                                  on_exit=self.on_exit_data_validation),
            self.INVALID_DATA: StateTableEntry('InvalidData',
                                               transits_to=[self.DESTROYED],
                                               on_enter=self.on_enter_invalid_data,
                                               on_exit=self.on_exit_invalid_data),
            self.COGNITION: StateTableEntry('Cognition',
                                            transits_to=[self.PARTIAL_RESULT, self.COMPLETED],
                                            on_enter=self.on_enter_cognition,
                                            on_exit=self.on_exit_cognition),
            self.PARTIAL_RESULT: StateTableEntry('PartialResult',
                                                 transits_to=[self.DESTROYED],
                                                 on_enter=self.on_enter_partial_result,
                                                 on_exit=self.on_exit_partial_result),
            self.COMPLETED: StateTableEntry('Completed',
                                            transits_to=[self.DESTROYED],
                                            on_enter=self.on_enter_completed,
                                            on_exit=self.on_exit_completed)
        }

        super().__init__(table=table, *args, **kwargs)

    def on_enter_state_uninitialized(self, from_state: int):
        pass

    def on_enter_state_destroyed(self, from_state: int):
        self.delegate.terminate_job(self)

    def on_enter_gathering_workers(self, from_state: int):
        pass

    def on_enter_insufficient_workers(self, from_state: int):
        pass

    def on_enter_data_validation(self, from_state: int):
        pass

    def on_enter_invalid_data(self, from_state: int):
        pass

    def on_enter_cognition(self, from_state: int):
        pass

    def on_enter_partial_result(self, from_state: int):
        pass

    def on_enter_completed(self, from_state: int):
        self.delegate.terminate_job(self)

    def on_exit_state_uninitialized(self, to_state: int):
        pass

    def on_exit_state_destroyed(self, to_state: int):
        pass

    def on_exit_gathering_workers(self, to_state: int):
        pass

    def on_exit_insufficient_workers(self, to_state: int):
        pass

    def on_exit_data_validation(self, to_state: int):
        pass

    def on_exit_invalid_data(self, to_state: int):
        pass

    def on_exit_cognition(self, to_state: int):
        pass

    def on_exit_partial_result(self, to_state: int):
        pass

    def on_exit_completed(self, to_state: int):
        pass

