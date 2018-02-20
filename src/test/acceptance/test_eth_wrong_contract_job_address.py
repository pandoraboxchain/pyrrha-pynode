import unittest

from patterns.exceptions import EmptyCognitiveJobInWorkerContract
from test.test_manager import TestManager

# for launch test NOT from console
# place path to config file to TestManager as '../../../pynode.ini' TestManager('../../../pynode.ini')
# and to pynode launcher self.manager.run_test_pynode('../../../pynode.ini')


class TestInitCognitiveJobContract(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        cls.manager = TestManager()
        cls.manager.get_configuration().set_default_values()
        cls.manager.get_configuration().empty_job_address = 1
        cls.manager.run_test_listener(demon=True)

    def test_wrong_contract_job_address(self):
        print('======================================================================= test_wrong_contract_job_address')
        self.assertRaises(EmptyCognitiveJobInWorkerContract, lambda: self.manager.run_test_pynode())

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


