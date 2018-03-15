import unittest

from patterns.exceptions import WrongContractAddressOrABI
from tests.test_launcher import TestManager


class TestInitWorkerContract(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        print('==================================================================== test_wrong_worker_contract_address')
        cls.manager = TestManager('../../pynode.ini')
        cls.manager.get_configuration().set_default_values(cls.manager.pandora_contract_address,
                                                           "0x5677db552d5fd9911a5560cb0bd40be90a70eff3")
                                                         # "0x5677db552d5fd9911a5560cb0bd40be90a70eff2"
        cls.manager.run_test_listener(demon=True)

    def test_wrong_worker_contract_address(self):
        try:
            self.manager.run_test_pynode()
        except Exception as ex:
            self.assertEqual(ex.__class__, WrongContractAddressOrABI)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


