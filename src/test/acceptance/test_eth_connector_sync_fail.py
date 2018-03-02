import unittest

from patterns.exceptions import EthIsNotInSyncException
from test.test_manager import TestManager


class TestEthNotInSyncStartup(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        print('======================================================================== test_eth_not_in_sync_exception')
        cls.manager = TestManager('../../../pynode.ini')
        cls.manager.get_configuration().set_default_values(cls.manager.pandora_contract_address,
                                                           cls.manager.worker_contract_address)
        cls.manager.get_configuration().eth_node_state = 1
        cls.manager.run_test_listener(demon=True)

    def test_eth_not_in_sync_exception(self):
        self.assertRaises(EthIsNotInSyncException, self.manager.run_test_pynode())

    @classmethod
    def tearDownClass(cls):
        cls.manager = None
