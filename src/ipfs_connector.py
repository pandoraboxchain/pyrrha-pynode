import ipfsapi


class IPFSConnector:

    def __init__(self, host: str='127.0.0.1', port: int=5001):
        self.api = ipfsapi.connect(host, port)

    def download_file(self, addr: str):
        return self.api.get(addr)
        # TODO: Docs say nothing about return value from get function and source code is not clear what it returns

    def upload_file(self, filename: str) -> str:
        res = self.api.add(filename)
        return res['Hash']
