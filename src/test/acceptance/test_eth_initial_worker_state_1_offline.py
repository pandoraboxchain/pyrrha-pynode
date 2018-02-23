import unittest

from test.test_manager import TestManager


class TestWorkerInitialStateOFFLINE(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        print('===================================================================== test_initial_worker_state_offline')
        cls.manager = TestManager('../../../pynode.ini')
        cls.manager.get_configuration().set_default_values(cls.manager.pandora_contract_address,
                                                           cls.manager.worker_contract_address)
        cls.manager.get_configuration().worker_state = 1
        # if set empty job in test mode EmptyCognitiveJobInWorkerContract is raises
        # cls.manager.get_configuration().empty_job_address = 1
        cls.manager.run_test_listener(demon=True)

    def test_initial_worker_state_offline(self):
        result = self.manager.run_test_pynode()
        self.assertTrue(result, 1)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


