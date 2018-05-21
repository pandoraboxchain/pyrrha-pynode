import unittest

from typing import Callable
from pynode.core.job.cognitive_job import CognitiveJob, CognitiveJobDelegate
from pynode.core.patterns.state_machine import StateTransitionError


class TestJob(unittest.TestCase, CognitiveJobDelegate):

    terminate_job_flag = 0
    transact_flag = 0

    def reset_flags(self):
        self.terminate_job_flag = 0
        self.transact_flag = 0

    # ------------------------------------
    # cognitive job delegate
    def terminate_job(self, job):
        self.terminate_job_flag = 1

    def transact(self, name: str, cb: Callable):
        self.transact_flag = 1

    # ------------------------------------
    # check all possible states changes for init state 0 = Uninitialized
    # true
    def test_job_state_0_to_1(self):
        # Uninitialized --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 0
        try:
            cognitive_job.state = 1
        except StateTransitionError:
            pass
        assert cognitive_job.state == 1

    # false
    def test_job_state_0_to_2(self):
        # Uninitialized --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 0
        with self.assertRaises(Exception):
            cognitive_job.state = 2

    # false
    def test_job_state_0_to_3(self):
        # Uninitialized --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 0
        with self.assertRaises(Exception):
            cognitive_job.state = 3

    # false
    def test_job_state_0_to_4(self):
        # Uninitialized --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 0
        with self.assertRaises(Exception):
            cognitive_job.state = 4

    # false
    def test_job_state_0_to_5(self):
        # Uninitialized --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 0
        with self.assertRaises(Exception):
            cognitive_job.state = 5

    # false
    def test_job_state_0_to_6(self):
        # Uninitialized --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 0
        with self.assertRaises(Exception):
            cognitive_job.state = 6

    # false
    def test_job_state_0_to_7(self):
        # Uninitialized --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 0
        with self.assertRaises(Exception):
            cognitive_job.state = 7

    # ------------------------------------
    # check all possible states changes for init state 1 = GatheringWorkers
    # false
    def test_job_state_1_to_1(self):
        # GatheringWorkers --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 1
        with self.assertRaises(Exception):
            cognitive_job.state = 1

    # true
    def test_job_state_1_to_2(self):
        # GatheringWorkers --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 1
        try:
            cognitive_job.state = 2
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 2

    # true
    def test_job_state_1_to_3(self):
        # GatheringWorkers --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 1
        try:
            cognitive_job.state = 3
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 3

    # false
    def test_job_state_1_to_4(self):
        # GatheringWorkers --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 1
        with self.assertRaises(Exception):
            cognitive_job.state = 4

    # false
    def test_job_state_1_to_5(self):
        # GatheringWorkers --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 1
        with self.assertRaises(Exception):
            cognitive_job.state = 5

    # false
    def test_job_state_1_to_6(self):
        # GatheringWorkers --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 1
        with self.assertRaises(Exception):
            cognitive_job.state = 6

    # false
    def test_job_state_1_to_7(self):
        # GatheringWorkers --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 1
        with self.assertRaises(Exception):
            cognitive_job.state = 7

    # ------------------------------------
    # check all possible states changes for init state 2 = InsufficientWorkers
    # false
    def test_job_state_2_to_1(self):
        # InsufficientWorkers --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        with self.assertRaises(Exception):
            cognitive_job.state = 1

    # false
    def test_job_state_2_to_2(self):
        # InsufficientWorkers --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        with self.assertRaises(Exception):
            cognitive_job.state = 2

    # false
    def test_job_state_2_to_3(self):
        # InsufficientWorkers --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        with self.assertRaises(Exception):
            cognitive_job.state = 3

    # false
    def test_job_state_2_to_4(self):
        # InsufficientWorkers --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        with self.assertRaises(Exception):
            cognitive_job.state = 4

    # false
    def test_job_state_2_to_5(self):
        # InsufficientWorkers --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        with self.assertRaises(Exception):
            cognitive_job.state = 5

    # false
    def test_job_state_2_to_6(self):
        # InsufficientWorkers --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        with self.assertRaises(Exception):
            cognitive_job.state = 6

    # false
    def test_job_state_2_to_7(self):
        # InsufficientWorkers --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        with self.assertRaises(Exception):
            cognitive_job.state = 7

    # true + TERMINATE_JOB
    def test_job_state_2_to_DESTROYED(self):
        # InsufficientWorkers --> DESTROYED
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 2
        try:
            cognitive_job.state = 0xFF
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 0xFF
        # validate callbacks
        assert self.terminate_job_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 3 = DataValidation
    # false
    def test_job_state_3_to_1(self):
        # DataValidation --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        with self.assertRaises(Exception):
            cognitive_job.state = 1

    # true
    def test_job_state_3_to_2(self):
        # DataValidation --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        try:
            cognitive_job.state = 2
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 2

    # false
    def test_job_state_3_to_3(self):
        # DataValidation --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        with self.assertRaises(Exception):
            cognitive_job.state = 3

    # true
    def test_job_state_3_to_4(self):
        # DataValidation --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        try:
            cognitive_job.state = 4
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 4

    # true
    def test_job_state_3_to_5(self):
        # DataValidation --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        try:
            cognitive_job.state = 5
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 5

    # false
    def test_job_state_3_to_6(self):
        # DataValidation --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        with self.assertRaises(Exception):
            cognitive_job.state = 6

    # false
    def test_job_state_3_to_7(self):
        # DataValidation --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        with self.assertRaises(Exception):
            cognitive_job.state = 7

    # true + TERMINATE_JOB
    def test_job_state_3_to_DESTROYED(self):
        # InsufficientWorkers --> DESTROYED
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 3
        try:
            cognitive_job.state = 0xFF
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 0xFF
        # validate callbacks
        assert self.terminate_job_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 4 = InvalidData
    # false
    def test_job_state_4_to_1(self):
        # InvalidData --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        with self.assertRaises(Exception):
            cognitive_job.state = 1

    # false
    def test_job_state_4_to_2(self):
        # InvalidData --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        with self.assertRaises(Exception):
            cognitive_job.state = 2

    # false
    def test_job_state_4_to_3(self):
        # InvalidData --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        with self.assertRaises(Exception):
            cognitive_job.state = 3

    # false
    def test_job_state_4_to_4(self):
        # InvalidData --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        with self.assertRaises(Exception):
            cognitive_job.state = 4

    # false
    def test_job_state_4_to_5(self):
        # InvalidData --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        with self.assertRaises(Exception):
            cognitive_job.state = 5

    # false
    def test_job_state_4_to_6(self):
        # InvalidData --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        with self.assertRaises(Exception):
            cognitive_job.state = 6

    # false
    def test_job_state_4_to_7(self):
        # InvalidData --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        with self.assertRaises(Exception):
            cognitive_job.state = 7

    # true + TERMINATE_JOB
    def test_job_state_3_to_DESTROYED(self):
        # InvalidData --> DESTROYED
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 4
        try:
            cognitive_job.state = 0xFF
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 0xFF
        # validate callbacks
        assert self.terminate_job_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 5 = Cognition
    # false
    def test_job_state_5_to_1(self):
        # Cognition --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 5
        with self.assertRaises(Exception):
            cognitive_job.state = 1

    # false
    def test_job_state_5_to_2(self):
        # Cognition --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 5
        with self.assertRaises(Exception):
            cognitive_job.state = 2

    # false
    def test_job_state_5_to_3(self):
        # Cognition --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 5
        with self.assertRaises(Exception):
            cognitive_job.state = 3

    # false
    def test_job_state_5_to_4(self):
        # Cognition --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 5
        with self.assertRaises(Exception):
            cognitive_job.state = 4

    # false
    def test_job_state_5_to_5(self):
        # Cognition --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 5
        with self.assertRaises(Exception):
            cognitive_job.state = 5

    # true
    def test_job_state_5_to_6(self):
        # Cognition --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 5
        try:
            cognitive_job.state = 6
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 6

    # true + TERMINATE_JOB
    def test_job_state_5_to_7(self):
        # Cognition --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 5
        try:
            cognitive_job.state = 7
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 7

    # ------------------------------------
    # check all possible states changes for init state 6 = PartialResult
    # false
    def test_job_state_6_to_1(self):
        # PartialResult --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        with self.assertRaises(Exception):
            cognitive_job.state = 1

    # false
    def test_job_state_6_to_2(self):
        # PartialResult --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        with self.assertRaises(Exception):
            cognitive_job.state = 2

    # false
    def test_job_state_6_to_3(self):
        # PartialResult --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        with self.assertRaises(Exception):
            cognitive_job.state = 3

    # false
    def test_job_state_6_to_4(self):
        # PartialResult --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        with self.assertRaises(Exception):
            cognitive_job.state = 4

    # false
    def test_job_state_6_to_5(self):
        # PartialResult --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        with self.assertRaises(Exception):
            cognitive_job.state = 5

    # false
    def test_job_state_6_to_6(self):
        # PartialResult --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        with self.assertRaises(Exception):
            cognitive_job.state = 6

    # false
    def test_job_state_6_to_7(self):
        # Cognition --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        with self.assertRaises(Exception):
            cognitive_job.state = 7

    # true + TERMINATE_JOB
    def test_job_state_6_to_DESTROYED(self):
        # InvalidData --> DESTROYED
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 6
        try:
            cognitive_job.state = 0xFF
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 0xFF
        # validate callbacks
        assert self.terminate_job_flag == 1

    # ------------------------------------
    # check all possible states changes for init state 7 = Completed
    # false + TERMINATE_JOB
    def test_job_state_7_to_1(self):
        # Completed --> GatheringWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        with self.assertRaises(Exception):
            cognitive_job.state = 1
        # validate callbacks
        assert self.terminate_job_flag == 1

    # false + TERMINATE_JOB
    def test_job_state_7_to_2(self):
        # Completed --> InsufficientWorkers
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        with self.assertRaises(Exception):
            cognitive_job.state = 2
        # validate callbacks
        assert self.terminate_job_flag == 1

    # false + TERMINATE_JOB
    def test_job_state_7_to_3(self):
        # Completed --> DataValidation
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        with self.assertRaises(Exception):
            cognitive_job.state = 3
        # validate callbacks
        assert self.terminate_job_flag == 1

    # false + TERMINATE_JOB
    def test_job_state_7_to_4(self):
        # Completed --> InvalidData
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        with self.assertRaises(Exception):
            cognitive_job.state = 4
        # validate callbacks
        assert self.terminate_job_flag == 1

    # false + TERMINATE_JOB
    def test_job_state_7_to_5(self):
        # Completed --> Cognition
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        with self.assertRaises(Exception):
            cognitive_job.state = 5
        # validate callbacks
        assert self.terminate_job_flag == 1

    # false + TERMINATE_JOB
    def test_job_state_7_to_6(self):
        # Completed --> PartialResult
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        with self.assertRaises(Exception):
            cognitive_job.state = 6
        # validate callbacks
        assert self.terminate_job_flag == 1

    # false + TERMINATE_JOB
    def test_job_state_7_to_7(self):
        # Completed --> Completed
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        with self.assertRaises(Exception):
            cognitive_job.state = 7
        # validate callbacks
        assert self.terminate_job_flag == 1

    # true + TERMINATE_JOB
    def test_job_state_7_to_DESTROYED(self):
        # Completed --> DESTROYED
        self.reset_flags()
        cognitive_job = CognitiveJob(delegate=self, contract_container='')
        cognitive_job.state = 7
        try:
            cognitive_job.state = 0xFF
        except StateTransitionError as ex:
            pass
        assert cognitive_job.state == 0xFF
        # validate callbacks
        assert self.terminate_job_flag == 1