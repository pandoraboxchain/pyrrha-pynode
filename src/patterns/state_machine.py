import logging
from typing import *


State = NewType('State', int)
StateCallback = Callable[[State], None]


class StateTableEntry:

    def __init__(self, name: str, on_enter: StateCallback, on_exit: StateCallback, transits_to: List[State]):
        self.__name = name
        self.__on_enter = on_enter
        self.__on_exit = on_exit
        self.__transits_to = transits_to

    @property
    def name(self) -> str:
        return self.__name

    @property
    def on_enter(self) -> StateCallback:
        return self.__on_enter

    @property
    def on_exit(self) -> StateCallback:
        return self.__on_exit

    @property
    def transits_to(self) -> List[State]:
        return self.__transits_to


StateTable = Dict[State, StateTableEntry]


class StateTransitionError(Exception):

    def __init__(self, from_state: State, to_state: State):
        super().__init__()
        self.from_state = from_state
        self.to_state = to_state


class StateMachine:

    def __init__(self, table: StateTable, force_rules: bool = True):
        self.__state = None
        self.__state_table = table
        self.force_rules = force_rules

    @property
    def state(self) -> State:
        return self.__state

    @state.setter
    def state(self, to_state: State):
        from_state = self.__state

        if from_state is not None:
            if to_state not in self.state_table[from_state].transits_to:
                if self.force_rules:
                    raise StateTransitionError(from_state=from_state, to_state=to_state)
                else:
                    logging.warning("Unregistered state transition from %s to %s",
                                    self.state_table[from_state].name, self.state_table[to_state].name)
                    return

            self.state_table[from_state].on_exit(to_state)

        self.__state = to_state
        self.state_table[to_state].on_enter(from_state)

    @property
    def state_table(self) -> StateTable:
        return self.__state_table
