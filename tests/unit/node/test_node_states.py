import unittest

from typing import Callable

from core.node.worker_node import WorkerNode, WorkerNodeDelegate
from core.patterns.state_machine import StateTransitionError


class TestNode(unittest.TestCase, WorkerNodeDelegate):
    create_cognitive_job_flag = 0
    start_validating_flag = 0
    start_computing_flag = 0
    state_transact_flag = 0

    def reset_flags(self):
        self.create_cognitive_job_flag = 0
        self.start_validating_flag = 0
        self.start_computing_flag = 0
        self.state_transact_flag = 0

    # ------------------------------------
    # worker node delegate
    job_address = None

    def create_cognitive_job(self):
        self.create_cognitive_job_flag = 1

    def start_validating(self):
        self.start_validating_flag = 1

    def start_computing(self):
        self.start_computing_flag = 1

    def state_transact(self, name: str):
        self.state_transact_flag = 1

    # ------------------------------------
    # check all possible states changes for init state 0 = Uninitialized
    # true + callbacks
    def test_worker_node_state_0_to_1(self):
        # Uninitialized --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1
        # callback flags
        assert self.state_transact_flag == 1

    # true
    def test_worker_node_state_0_to_2(self):
        # Uninitialized --> IDLE
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2

    # false
    def test_worker_node_state_0_to_3(self):
        # Uninitialized --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 0
            assert ex.to_state == 3

    # false
    def test_worker_node_state_0_to_4(self):
        # Uninitialized --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 0
            assert ex.to_state == 4

    # false
    def test_worker_node_state_0_to_5(self):
        # Uninitialized --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 0
            assert ex.to_state == 5

    # false
    def test_worker_node_state_0_to_6(self):
        # Uninitialized --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 0
            assert ex.to_state == 6

    # false
    def test_worker_node_state_0_to_7(self):
        # Uninitialized --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 0
            assert ex.to_state == 7

    # true
    def test_worker_node_state_0_to_8(self):
        # Uninitialized --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 8
        except StateTransitionError:
            pass
        assert worker_node.state == 8

    # false
    def test_worker_node_state_0_to_9(self):
        # Uninitialized --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 0
        try:
            worker_node.state = 9
        except StateTransitionError as ex:
            assert ex.from_state == 0
            assert ex.to_state == 9

    # ------------------------------------
    # check all possible states changes for init state 1 = Offline
    # false + callbacks
    def test_worker_node_state_1_to_0(self):
        # Offline --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 0
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_1(self):
        # Offline --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 1
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 1
        # transact ALIVE
        assert self.state_transact_flag == 1

    # true + callbacks
    def test_worker_node_state_1_to_2(self):
        # Offline --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_3(self):
        # Offline --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 3
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_4(self):
        # Offline --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 4
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_5(self):
        # Offline --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 5
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_6(self):
        # Offline --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 6
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_7(self):
        # Offline --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 7
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_8(self):
        # Offline --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 8
        # transact ALIVE
        assert self.state_transact_flag == 1

    # false + callbacks
    def test_worker_node_state_1_to_9(self):
        # Offline --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 1
        try:
            worker_node.state = 9
        except StateTransitionError as ex:
            assert ex.from_state == 1
            assert ex.to_state == 9
        # transact ALIVE
        assert self.state_transact_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 2 = Idle
    # false
    def test_worker_node_state_2_to_0(self):
        # Idle --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.from_state == 2
            assert ex.to_state == 0

    # true
    def test_worker_node_state_2_to_1(self):
        # Idle --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1

        # transact ALIVE
        assert self.state_transact_flag == 1

    # false
    def test_worker_node_state_2_to_2(self):
        # Idle --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 2
        except StateTransitionError as ex:
            assert ex.from_state == 2
            assert ex.to_state == 2

    # true + CREATE COGNITIVE JOB
    def test_worker_node_state_2_to_3(self):
        # Idle --> Assigned
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 3
        except StateTransitionError:
            pass
        assert worker_node.state == 3
        # CREATE COGNITIVE JOB CALLBACK
        assert self.create_cognitive_job_flag == 1

    # false
    def test_worker_node_state_2_to_4(self):
        # Idle --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 2
            assert ex.to_state == 4

    # false
    def test_worker_node_state_2_to_5(self):
        # Idle --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 2
            assert ex.to_state == 5

    # false
    def test_worker_node_state_2_to_6(self):
        # Idle --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 2
            assert ex.to_state == 6

    # false
    def test_worker_node_state_2_to_7(self):
        # Idle --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 2
            assert ex.to_state == 7

    # false
    def test_worker_node_state_2_to_8(self):
        # Idle --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 2
            assert ex.to_state == 8

    # true
    def test_worker_node_state_2_to_9(self):
        # Idle --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 2
        try:
            worker_node.state = 9
        except StateTransitionError:
            pass
        assert worker_node.state == 9

    # ------------------------------------
    # check all possible states changes for init state 3 = Assigned
    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_0(self):
        # Assigned --> Uninitialized
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.to_state == 0
            assert ex.from_state == 3

        # CREATE COGNITIVE JOB CALLBACK
        assert self.create_cognitive_job_flag == 1

    # true + CREATE COGNITIVE JOB + ALIVE
    def test_worker_node_state_3_to_1(self):
        # Assigned --> Offline
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1

        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_2(self):
        # Assigned --> Idle
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 2
        except StateTransitionError as ex:
            assert ex.from_state == 3
            assert ex.to_state == 2

        assert self.create_cognitive_job_flag == 1

    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_3(self):
        # Assigned --> Assigned
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 3
            assert ex.to_state == 3

        assert self.create_cognitive_job_flag == 1

    # true + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_3_to_4(self):
        # Assigned --> ReadyForDataValidation
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 4
        except StateTransitionError:
            pass
        assert worker_node.state == 4
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_5(self):
        # Assigned --> ValidatingData
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 3
            assert ex.to_state == 5

        assert self.create_cognitive_job_flag == 1

    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_6(self):
        # Assigned --> ReadyForComputing
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 3
            assert ex.to_state == 6

        assert self.create_cognitive_job_flag == 1

    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_7(self):
        # Assigned --> Computing
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 3
            assert ex.to_state == 7

        assert self.create_cognitive_job_flag == 1

    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_8(self):
        # Assigned --> InsufficientStake
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 3
            assert ex.to_state == 8

        assert self.create_cognitive_job_flag == 1

    # false + CREATE COGNITIVE JOB
    def test_worker_node_state_3_to_9(self):
        # Assigned --> UnderPenalty
        self.reset_flags()
        self.job_id_hex = ''
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 3
        try:
            worker_node.state = 9
        except StateTransitionError as ex:
            assert ex.from_state == 3
            assert ex.to_state == 9

        assert self.create_cognitive_job_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 4 = ReadyForDataValidation
    # false + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_0(self):
        # ReadyForDataValidation --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.from_state == 4
            assert ex.to_state == 0

        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # true + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION + ALIVE
    def test_worker_node_state_4_to_1(self):
        # ReadyForDataValidation --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1

        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # true + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_2(self):
        # ReadyForDataValidation --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2

        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_3(self):
        # ReadyForDataValidation --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 4
            assert ex.to_state == 3

        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_4(self):
        # ReadyForDataValidation --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 4
            assert ex.to_state == 4
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # true + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION + VALIDATING_DATA
    def test_worker_node_state_4_to_5(self):
        # ReadyForDataValidation --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 5
        except StateTransitionError:
            pass
        assert worker_node.state == 5
        # validate callbacks
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_6(self):
        # ReadyForDataValidation --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 4
            assert ex.to_state == 6
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_7(self):
        # ReadyForDataValidation --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 4
            assert ex.to_state == 7

        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_8(self):
        # ReadyForDataValidation --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 4
            assert ex.to_state == 8
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # true + CREATE COGNITIVE JOB + PROCESS_TO_DATA_VALIDATION
    def test_worker_node_state_4_to_9(self):
        # ReadyForDataValidation --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 4
        try:
            worker_node.state = 9
        except StateTransitionError:
            pass
        assert worker_node.state == 9
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.state_transact_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 5 = ValidatingData
    # false + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_0(self):
        # ValidatingData --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.from_state == 5
            assert ex.to_state == 0
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # true + CREATE COGNITIVE JOB + START_VALIDATING + TRANSACT_ALIVE
    def test_worker_node_state_5_to_1(self):
        # ValidatingData --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1
        assert self.state_transact_flag == 1

    # true + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_2(self):
        # ValidatingData --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # false + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_3(self):
        # ValidatingData --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 5
            assert ex.to_state == 3
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # false + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_4(self):
        # ValidatingData --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 5
            assert ex.to_state == 4
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # false + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_5(self):
        # ValidatingData --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 5
            assert ex.to_state == 5
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # true + CREATE COGNITIVE JOB + START_VALIDATING + PROCESS_TO_COGNITION
    def test_worker_node_state_5_to_6(self):
        # ValidatingData --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 6
        except StateTransitionError:
            pass
        assert worker_node.state == 6
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1
        assert self.state_transact_flag == 1

    # false + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_7(self):
        # ValidatingData --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 5
            assert ex.to_state == 7
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # false + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_8(self):
        # ValidatingData --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 5
            assert ex.to_state == 8
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # true + CREATE COGNITIVE JOB + START_VALIDATING
    def test_worker_node_state_5_to_9(self):
        # ValidatingData --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 9
        except StateTransitionError:
            pass
        assert worker_node.state == 9
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 6 = ReadyForComputing
    # false + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_0(self):
        # ReadyForComputing --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.to_state == 0
            assert ex.from_state == 6
        # validate callbacks called
        assert self.state_transact_flag == 1

    # true + PROCESS_TO_COGNITION + ALIVE
    def test_worker_node_state_6_to_1(self):
        # ReadyForComputing --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1
        # validate callbacks called
        assert self.state_transact_flag == 1

    # true + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_2(self):
        # ReadyForComputing --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2
        # validate callbacks called
        assert self.state_transact_flag == 1

    # false + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_3(self):
        # ReadyForComputing --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 6
            assert ex.to_state == 3
        # validate callbacks called
        assert self.state_transact_flag == 1

    # false + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_4(self):
        # ReadyForComputing --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 6
            assert ex.to_state == 4
        # validate callbacks called
        assert self.state_transact_flag == 1

    # false + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_5(self):
        # ReadyForComputing --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 6
            assert ex.to_state == 5
        # validate callbacks called
        assert self.state_transact_flag == 1

    # false + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_6(self):
        # ReadyForComputing --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 6
            assert ex.to_state == 6
        # validate callbacks called
        assert self.state_transact_flag == 1

    # true + PROCESS_TO_COGNITION + START_COMPUTING
    def test_worker_node_state_6_to_7(self):
        # ReadyForComputing --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 7
        except StateTransitionError:
            pass
        assert worker_node.state == 7
        # validate callbacks called
        assert self.state_transact_flag == 1
        assert self.start_computing_flag == 1

    # false + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_8(self):
        # ReadyForComputing --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 6
            assert ex.to_state == 8
        # validate callbacks called
        assert self.state_transact_flag == 1

    # true + PROCESS_TO_COGNITION
    def test_worker_node_state_6_to_9(self):
        # ReadyForComputing --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 6
        try:
            worker_node.state = 9
        except StateTransitionError:
            pass
        assert worker_node.state == 9
        # validate callbacks called
        assert self.state_transact_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 7 = Computing
    # false + START_COMPUTING
    def test_worker_node_state_7_to_0(self):
        # Computing --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.from_state == 7
            assert ex.to_state == 0
        # validate callbacks called
        assert self.start_computing_flag == 1

    # true + START_COMPUTING + ALIVE
    def test_worker_node_state_7_to_1(self):
        # Computing --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1
        # validate callbacks called
        assert self.start_computing_flag == 1
        assert self.state_transact_flag == 1

    # true + START_COMPUTING
    def test_worker_node_state_7_to_2(self):
        # Computing --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2
        # validate callbacks called
        assert self.start_computing_flag == 1

    # false + START_COMPUTING
    def test_worker_node_state_7_to_3(self):
        # Computing --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 7
            assert ex.to_state == 3
        # validate callbacks called
        assert self.start_computing_flag == 1

    # false + START_COMPUTING
    def test_worker_node_state_7_to_4(self):
        # Computing --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 7
            assert ex.to_state == 4
        # validate callbacks called
        assert self.start_computing_flag == 1

    # false + START_COMPUTING
    def test_worker_node_state_7_to_5(self):
        # Computing --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 7
            assert ex.to_state == 5
        # validate callbacks called
        assert self.start_computing_flag == 1

    # false + START_COMPUTING
    def test_worker_node_state_7_to_6(self):
        # Computing --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 7
            assert ex.to_state == 6
        # validate callbacks called
        assert self.start_computing_flag == 1

    # false + START_COMPUTING
    def test_worker_node_state_7_to_7(self):
        # Computing --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 7
            assert ex.to_state == 7
        # validate callbacks called
        assert self.start_computing_flag == 1

    # false + START_COMPUTING
    def test_worker_node_state_7_to_8(self):
        # Computing --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 7
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 7
            assert ex.to_state == 8
        # validate callbacks called
        assert self.start_computing_flag == 1

    # true + CREATE_COGNITIVE_JOB + START_VALIDATING
    def test_worker_node_state_7_to_9(self):
        # Computing --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 5
        try:
            worker_node.state = 9
        except StateTransitionError:
            pass
        assert worker_node.state == 9
        # validate callbacks called
        assert self.create_cognitive_job_flag == 1
        assert self.start_validating_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 8 = InsufficientStake
    # false
    def test_worker_node_state_8_to_0(self):
        # InsufficientStake --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 0

    # true + ALIVE
    def test_worker_node_state_8_to_1(self):
        # InsufficientStake --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1
        # validate callbacks called
        assert self.state_transact_flag == 1

    # true
    def test_worker_node_state_8_to_2(self):
        # InsufficientStake --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2

    # false
    def test_worker_node_state_8_to_3(self):
        # InsufficientStake --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 3

    # false
    def test_worker_node_state_8_to_4(self):
        # InsufficientStake --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 4

    # false
    def test_worker_node_state_8_to_5(self):
        # InsufficientStake --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 5

    # false
    def test_worker_node_state_8_to_6(self):
        # InsufficientStake --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 6

    # false
    def test_worker_node_state_8_to_7(self):
        # InsufficientStake --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 7

    # false
    def test_worker_node_state_8_to_8(self):
        # InsufficientStake --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 8
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 8

    # false
    def test_worker_node_state_8_to_9(self):
        # InsufficientStake --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 8
        try:
            worker_node.state = 9
        except StateTransitionError as ex:
            assert ex.from_state == 8
            assert ex.to_state == 9

    # ------------------------------------
    # check all possible states changes for init state 9 = UnderPenalty
    # false
    def test_worker_node_state_9_to_0(self):
        # UnderPenalty --> Uninitialized
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 0
        except StateTransitionError as ex:
            assert ex.from_state == 9
            assert ex.to_state == 0

    # true + ALIVE
    def test_worker_node_state_9_to_1(self):
        # UnderPenalty --> Offline
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 1
        except StateTransitionError:
            pass
        assert worker_node.state == 1
        # validate callbacks called
        assert self.state_transact_flag == 1

    # true
    def test_worker_node_state_9_to_2(self):
        # UnderPenalty --> Idle
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 2
        except StateTransitionError:
            pass
        assert worker_node.state == 2

    # false
    def test_worker_node_state_9_to_3(self):
        # UnderPenalty --> Assigned
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 3
        except StateTransitionError as ex:
            assert ex.from_state == 9
            assert ex.to_state == 3

    # false
    def test_worker_node_state_9_to_4(self):
        # UnderPenalty --> ReadyForDataValidation
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 4
        except StateTransitionError as ex:
            assert ex.from_state == 9
            assert ex.to_state == 4

    # false
    def test_worker_node_state_9_to_5(self):
        # UnderPenalty --> ValidatingData
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 5
        except StateTransitionError as ex:
            assert ex.from_state == 9
            assert ex.to_state == 5

    # false
    def test_worker_node_state_9_to_6(self):
        # UnderPenalty --> ReadyForComputing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 6
        except StateTransitionError as ex:
            assert ex.from_state == 9
            assert ex.to_state == 6

    # false
    def test_worker_node_state_9_to_7(self):
        # UnderPenalty --> Computing
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 7
        except StateTransitionError as ex:
            assert ex.from_state == 9
            assert ex.to_state == 7

    # true
    def test_worker_node_state_9_to_8(self):
        # UnderPenalty --> InsufficientStake
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 8
        except StateTransitionError:
            pass
        assert worker_node.state == 8

    # false
    def test_worker_node_state_9_to_9(self):
        # UnderPenalty --> UnderPenalty
        self.reset_flags()
        worker_node = WorkerNode(delegate=self, contract_container='')
        worker_node.state = 9
        try:
            worker_node.state = 9
        except StateTransitionError as ex:
            assert ex.from_state == 9
            assert ex.to_state == 9


