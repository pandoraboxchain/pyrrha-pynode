import unittest

from patterns.exceptions import EthIsNotInSyncException
from tests.test_launcher import TestManager


class TestEthNotInSyncStartup(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        print('======================================================================== test_eth_not_in_sync_exception')
        cls.manager = TestManager('../../pynode.ini')
        cls.manager.get_configuration().set_default_values(cls.manager.pandora_contract_address,
                                                           cls.manager.worker_contract_address)
        cls.manager.get_configuration().eth_node_state = 1
        cls.manager.run_test_listener(demon=True)

    def test_eth_not_in_sync_exception(self):
        try:
            self.manager.run_test_pynode()
        except Exception as ex:
            self.assertEquals(ex.__class__, EthIsNotInSyncException)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None
