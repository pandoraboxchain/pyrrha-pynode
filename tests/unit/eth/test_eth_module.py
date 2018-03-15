import unittest
import logging

from web3 import Web3
from eth.eth_connector import EthConnector
from manager import Manager
from tests.test_launcher import TestManager
from patterns.exceptions import EthConnectionException, \
                                EthIsNotInSyncException, \
                                NotInitialized, \
                                WrongContractAddressOrABI


@unittest.skip("VERY IRRATIONAL")
class TestETHModule(unittest.TestCase):

    manager = None
    eth_connector = None
    mock_service = None

    @classmethod
    def setUpClass(cls):
        EthConnector.logger = logging.getLogger("test_eth_connector")
        cls.eth_connector = EthConnector('', '')
        cls.manager = Manager.get_instance()
        cls.mock_service = TestManager('../../../pynode.ini')

    @classmethod
    def tearDown(cls):
        pass

# -------------------------------
#  EthConnector connect() tests
# -------------------------------
    def test_eth_connector_return_true_on_web3_ready(self):
        self.manager.launch_mode = 0
        EthConnector.web3 = Web3('test_provider')
        # TODO The test passes, but it may be necessary to refactor the connector for more control
        assert self.eth_connector.connect() is True

    def test_eth_connector_raise_connection_exception(self):
        self.manager.launch_mode = 1
        EthConnector.server = "http://wrong_address:0000"
        try:
            self.eth_connector.connect()
        except Exception as ex:
            assert ex.__class__ is EthConnectionException

    def test_eth_connector_raise_sync_exception(self):
        self.manager.launch_mode = 1
        self.mock_service.get_configuration().set_default_values(self.mock_service.pandora_contract_address,
                                                                 self.mock_service.worker_contract_address)
        self.mock_service.get_configuration().eth_node_state = 1
        self.mock_service.run_test_listener(demon=False)
        try:
            EthConnector.server = "http://localhost:4000"
            self.eth_connector.connect()
        except Exception as ex:
            self.mock_service.stop_test_listener()
            assert ex.__class__ is EthIsNotInSyncException

    def test_eth_connector_success_connection(self):
        self.manager.launch_mode = 1
        self.mock_service.get_configuration().set_default_values(self.mock_service.pandora_contract_address,
                                                                 self.mock_service.worker_contract_address)
        self.mock_service.get_configuration().eth_node_state = 0
        self.mock_service.run_test_listener(demon=False)
        try:
            EthConnector.server = "http://localhost:4000"
            assert self.eth_connector.connect() is True
        except Exception as ex:
            print('test_eth_connector_connection_success : exception :' + str(ex))
        self.mock_service.stop_test_listener()

# -------------------------------
#  EthConnector init_contract() tests
# -------------------------------
    def test_init_contract_web3_not_initialized(self):
        try:
            self.eth_connector.init_contract()
        except Exception as ex:
            assert ex.__class__ is NotInitialized

    def test_init_contract_getting_contract_exception(self):
        self.manager.launch_mode = 1
        self.mock_service.get_configuration().set_default_values("0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe5",
                                                                 self.mock_service.worker_contract_address)
        self.mock_service.get_configuration().eth_node_state = 0
        self.mock_service.run_test_listener(demon=False)
        try:
            self.eth_connector = EthConnector(self.mock_service.pandora_contract_address,
                                              self.manager.eth_pandora_contract)
            EthConnector.server = "http://localhost:4000"
            self.eth_connector.connect()
            self.eth_connector.init_contract()
        except Exception as ex:
            self.mock_service.stop_test_listener()
            assert ex.__class__ is WrongContractAddressOrABI

