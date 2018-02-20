import unittest

from patterns.exceptions import WrongContractAddressOrABI
from test.test_manager import TestManager

# for launch test NOT from console
# place path to config file to TestManager as '../../../pynode.ini' TestManager('../../../pynode.ini')
# and to pynode launcher self.manager.run_test_pynode('../../../pynode.ini')


class TestInitWorkerContract(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        cls.manager = TestManager()
        cls.manager.get_configuration().set_default_values()# "0x5677db552d5fd9911a5560cb0bd40be90a70eff2"
        cls.manager.get_configuration().worker_node_address = "0x5677db552d5fd9911a5560cb0bd40be90a70eff3"
        cls.manager.run_test_listener(demon=True)

    def test_wrong_worker_contract_address(self):
        print('==================================================================== test_wrong_worker_contract_address')
        self.assertRaises(WrongContractAddressOrABI, lambda: self.manager.run_test_pynode())

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


