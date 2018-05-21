import logging
from pynode.integration.ipfs_service import IpfsAbstract


class IpfsConnectorDummy(IpfsAbstract):

    logger = logging.getLogger('IpfsConnectorDummy')

    def connect(self, server='localhost', port=5001, data_dir='../tmp'):
        pass

    def download_file(self, file_address: str):
        pass

    def upload_file(self, file_name: str):
        pass


