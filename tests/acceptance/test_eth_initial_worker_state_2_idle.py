import unittest

from tests.test_launcher import TestManager


class TestWorkerInitialStateIDLE(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        print('======================================================================== test_initial_worker_state_idle')
        cls.manager = TestManager('../../pynode.ini')
        cls.manager.get_configuration().set_default_values(cls.manager.pandora_contract_address,
                                                           cls.manager.worker_contract_address)
        cls.manager.get_configuration().worker_state = 2
        cls.manager.run_test_listener(demon=True)

    def test_initial_worker_state_idle(self):
        # launch pynode
        result = self.manager.run_test_pynode()
        self.assertTrue(result, 1)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


