from collections import namedtuple
import ipfsapi


IPFSConfig = namedtuple('IPFSConfig', 'server port')


class IPFSConnector:

    def __init__(self, config: IPFSConfig):
        self.config = config
        self.api = ipfsapi.connect(self.config.server, self.config.port)

    def download_file(self, addr: str):
        return self.api.get(addr)
        # TODO: Docs say nothing about return value from get function and source code is not clear what it returns

    def upload_file(self, filename: str) -> str:
        res = self.api.add(filename)
        return res['Hash']
