import unittest

from patterns.exceptions import EthIsNotInSyncException
from patterns.singleton import Singleton
from test.core.base_test_core import BaseCoreConfiguration
from test.test_manager import TestManager

# for launch test NOT from console
# place path to config file to TestManager as '../../../pynode.ini' TestManager('../../../pynode.ini')
# and to pynode launcher self.manager.run_test_pynode('../../../pynode.ini')


class TestEthNotInSyncStartup(unittest.TestCase):
    manager = None

    @classmethod
    def setUpClass(cls):
        cls.manager = TestManager()
        cls.manager.get_configuration().set_default_values()
        cls.manager.get_configuration().eth_node_state = 1
        cls.manager.run_test_listener(demon=True)

    def test_eth_not_in_sync_exception(self):
        print('======================================================================== test_eth_not_in_sync_exception')
        self.assertRaises(EthIsNotInSyncException, lambda: self.manager.run_test_pynode())

    @classmethod
    def tearDownClass(cls):
        cls.manager = None
