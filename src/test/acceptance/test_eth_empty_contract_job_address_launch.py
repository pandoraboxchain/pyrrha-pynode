import unittest

from test.test_manager import TestManager


class TestInitCognitiveJobContract(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        print('======================================================================= test_wrong_contract_job_address')
        cls.manager = TestManager('../../../pynode.ini')
        cls.manager.get_configuration().set_default_values(cls.manager.pandora_contract_address,
                                                           cls.manager.worker_contract_address)
        cls.manager.get_configuration().empty_job_address = 1
        cls.manager.run_test_listener(demon=True)

    def test_empty_contract_job_address(self):
        result = self.manager.run_test_pynode()
        # expect normal launch with empty job in worker contract
        self.assertTrue(result, 1)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


