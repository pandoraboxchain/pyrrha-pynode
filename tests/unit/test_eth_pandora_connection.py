import unittest
import logging
import mock

from manager import Manager
from tests.test_launcher import TestManager
from eth.eth_connector import EthConnector
from patterns.exceptions import EthConnectionException, \
                                EthIsNotInSyncException, \
                                ErrorContractGettingException, \
                                WrongContractAddressOrABI


class TestEthPandora(unittest.TestCase):

    manager = None
    pandora_connector = None
    mock_service = None

    @classmethod
    def setUpClass(cls):
        cls.manager = Manager.get_instance()
        cls.mock_service = TestManager('../../pynode.ini')
        cls.manager.launch_mode = 1
        EthConnector.logger = logging.getLogger("Broker")
        cls.pandora_connector = EthConnector(address=cls.manager.eth_pandora,
                                             contract=cls.manager.eth_pandora_contract)

    def test_eth_connector_unable_to_connect(self):
        try:
            EthConnector.server = 'http://localhost:4000'
            self.pandora_connector.connect()
        except Exception as ex:
            assert ex.__class__ is EthConnectionException

    @mock.patch('eth.eth_connector.EthConnector.call_eth_syncing', autospec=False)
    def test_eth_connector_is_syncing(self, fake_syncing):
        fake_syncing.side_effect = self.fake_eth_syncing_true_result()
        try:
            EthConnector.server = 'http://localhost:4000'
            assert self.pandora_connector.connect() is False
        except Exception as ex:
            assert ex.__class__ is EthIsNotInSyncException

    @mock.patch('eth.eth_connector.EthConnector.call_eth_syncing', autospec=False)
    def test_eth_connector_connect_success(self, fake_syncing):
        fake_syncing.side_effect = self.fake_eth_syncing_false_result()
        EthConnector.server = 'http://localhost:4000'
        assert self.pandora_connector.connect() is True

    @mock.patch('eth.eth_connector.EthConnector.call_eth_syncing', autospec=False)
    def test_eth_connector_init_contract_error_getting_contract(self, fake_syncing):
        fake_syncing.side_effect = self.fake_eth_syncing_false_result()
        try:
            EthConnector.server = 'http://localhost:4000'
            self.pandora_connector.connect()
            # As it turned out, the initialization of the contract only verifies the address to be plausible
            self.pandora_connector.address = "0x0"
            self.pandora_connector.init_contract()
        except Exception as ex:
            assert ex.__class__ is ErrorContractGettingException

    @mock.patch('eth.eth_connector.EthConnector.call_eth_syncing', autospec=False)
    def test_eth_connector_init_contract_error_call_owner(self, fake_syncing):
        fake_syncing.side_effect = self.fake_eth_syncing_false_result()
        try:
            EthConnector.server = 'http://localhost:4000'
            self.pandora_connector.connect()
            self.pandora_connector.init_contract()
        except Exception as ex:
            assert ex.__class__ is WrongContractAddressOrABI

    @mock.patch('eth.eth_connector.EthConnector.call_eth_syncing', autospec=False)
    @mock.patch('eth.eth_connector.EthConnector.call_eth_owner', autospec=False)
    def test_eth_connector_init_contract_success(self, fake_syncing, fake_owner):
        fake_syncing.side_effect = self.fake_eth_syncing_false_result()
        fake_owner.side_effect = self.fake_eth_owner_getting_success()
        EthConnector.server = 'http://localhost:4000'
        self.pandora_connector.address = self.manager.eth_pandora
        self.pandora_connector.connect()
        assert self.pandora_connector.init_contract() is True


# --------------------------------
# mock ethereum methods
# --------------------------------

    @staticmethod
    def fake_eth_syncing_true_result():
        return {"startingBlock": '0x384',
                "currentBlock": '0x386',
                "highestBlock": '0x454'}

    @staticmethod
    def fake_eth_syncing_false_result():
        return {False}

    @staticmethod
    def fake_eth_owner_getting_success():
        return {False}
