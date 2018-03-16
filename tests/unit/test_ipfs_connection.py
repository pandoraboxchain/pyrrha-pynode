import unittest
import mock
import ipfsapi

from ipfs.ipfs_connector import IPFSConnector


class TestIpfsPandora(unittest.TestCase):

    ipfs_connector = None

    @classmethod
    def setUpClass(cls):
        # TODO this is real ipfs address
        cls.ipfs_connector = IPFSConnector('ipfs.pandora.network', 5001, '../tmp')

    def test_connection_fail(self):
        try:
            self.ipfs_connector.server = 'localhost'
            self.ipfs_connector.connect()
        except Exception as ex:
            assert ex.__class__ is ipfsapi.exceptions.ConnectionError

    def test_connection_success(self):
        self.ipfs_connector.server = 'ipfs.pandora.network'
        self.ipfs_connector.connect()
        assert self.ipfs_connector.ipfs is not None



