import unittest

from patterns.exceptions import WrongContractAddressOrABI
from tests.test_launcher import TestManager


class TestInitPandoraContract(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        print('================================================================= test_wrong_pandora_contract_addresses')
        cls.manager = TestManager('../../pynode.ini')    # "0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe4"
        cls.manager.get_configuration().set_default_values("0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe5",
                                                           cls.manager.worker_contract_address)
        cls.manager.run_test_listener(demon=True)

    def test_wrong_pandora_contract_addresses(self):
        try:
            self.manager.run_test_pynode()
        except Exception as ex:
            self.assertEqual(ex.__class__, WrongContractAddressOrABI)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None
