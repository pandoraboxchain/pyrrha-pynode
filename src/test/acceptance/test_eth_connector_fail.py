import unittest

from patterns.exceptions import EthConnectionException
from test.test_manager import TestManager


class TestEthConnectionException(unittest.TestCase):

    def test_eth_unable_to_connect(self):
        self.manager = TestManager()
        print('============================================================================ test_eth_unable_to_connect')
        self.assertRaises(EthConnectionException, self.manager.run_test_pynode())

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


