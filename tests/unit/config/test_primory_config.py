import unittest

from configparser import ConfigParser


@unittest.skip("disable for travis")
class BaseConfigurationTest(unittest.TestCase):

    config_parser = None
    # path for single launch
    # default_config_path = '../../../pynode/core/config/pynode.ini'
    default_config_path = 'core/config/pynode.ini'

    @classmethod
    def setUpClass(cls):
        cls.config_parser = ConfigParser()

    def test_config_file_exist_and_valid(self):
        try:
            self.config_parser.read(self.default_config_path)
        except Exception as ex:
            print('Exception, default config file missing.')
            return

        assert self.config_parser is not None

        try:
            eth_section = self.config_parser['Ethereum']
            account_section = self.config_parser['Account']
            eth_contracts = self.config_parser['Contracts']
            ipfs_section = self.config_parser['IPFS']
            web_section = self.config_parser['Web']
        except Exception as ex:
            print('Missing config block in default config file.')
            print(ex)
            assert eth_section is not None
            assert account_section is not None
            assert eth_contracts is not None
            assert ipfs_section is not None
            assert web_section is not None

        assert eth_section['remote'] is not ''
        assert account_section['worker_node_account'] is not ''

        assert eth_contracts['pandora'] is not ''
        assert eth_contracts['worker_node'] is not ''
        assert eth_contracts['hooks'] is not ''
        assert eth_contracts['abi_path'] is not ''
        assert eth_contracts['start_on_launch'] is not ''

        assert ipfs_section['store_in'] is not ''
        ipfs_section_pandora = self.config_parser['IPFS.pandora']
        assert ipfs_section_pandora['server'] is not ''
        assert ipfs_section_pandora['port'] is not ''

        assert web_section['enable'] is not ''
        assert web_section['host'] is not ''
        assert web_section['port'] is not ''
        assert web_section['connections'] is not ''


