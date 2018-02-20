import unittest

from patterns.exceptions import WrongContractAddressOrABI
from test.test_manager import TestManager

# for launch test NOT from console
# place path to config file to TestManager as '../../../pynode.ini' TestManager('../../../pynode.ini')
# and to pynode launcher self.manager.run_test_pynode('../../../pynode.ini')


class TestInitPandoraContract(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        cls.manager = TestManager()
        cls.manager.get_configuration().set_default_values()  # "0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe4"
        cls.manager.get_configuration().pandora_hooks_address = "0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe5"
        cls.manager.run_test_listener(demon=True)

    def test_wrong_pandora_contract_addresses(self):
        print('================================================================= test_wrong_pandora_contract_addresses')
        self.assertRaises(WrongContractAddressOrABI, lambda: self.manager.run_test_pynode())

    @classmethod
    def tearDownClass(cls):
        cls.manager = None
