import unittest

from patterns.exceptions import EthConnectionException
from tests.test_launcher import TestManager


class TestEthConnectionException(unittest.TestCase):

    def test_eth_unable_to_connect(self):
        self.manager = TestManager('../../pynode.ini')
        print('============================================================================ test_eth_unable_to_connect')
        try:
            self.manager.run_test_pynode()
        except Exception as ex:
            self.assertEqual(ex.__class__, EthConnectionException)

    @classmethod
    def tearDownClass(cls):
        cls.manager = None


