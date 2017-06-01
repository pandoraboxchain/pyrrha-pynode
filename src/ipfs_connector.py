import os
from collections import namedtuple
import ipfsapi


IPFSConfig = namedtuple('IPFSConfig', 'server port data_path')


class IPFSConnector:

    def __init__(self, config: IPFSConfig):
        self.config = config
        self.api = ipfsapi.connect(self.config.server, self.config.port)

    def download_file(self, addr: str):
        os.chdir(self.config.data_path)
        return self.api.get(addr)
        # TODO: Docs say nothing about return value from get function and source code is not clear what it returns

    def upload_file(self, filename: str) -> str:
        os.chdir(self.config.data_path)
        res = self.api.add(filename)
        return res['Hash']
