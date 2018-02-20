import unittest

from patterns.exceptions import EthConnectionException
from patterns.singleton import Singleton
from test.test_manager import TestManager


# for launch test NOT from console
# place path to config file to TestManager as '../../../pynode.ini' TestManager('../../../pynode.ini')
# and to pynode launcher self.manager.run_test_pynode('../../../pynode.ini')

class TestEthConnectionException(unittest.TestCase):

    def test_eth_unable_to_connect(self):
        self.manager = TestManager()
        print('============================================================================ test_eth_unable_to_connect')
        self.assertRaises(EthConnectionException, lambda: self.manager.run_test_pynode())

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


