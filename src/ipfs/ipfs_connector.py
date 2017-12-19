import ipfsapi
import os

class IPFSConnector:

    def __init__(self, server: str, port: int, data_dir: str):
        self.server = server
        self.port = port
        self.data_dir = data_dir

        self.ipfs = None

    def connect(self):
        self.ipfs = ipfsapi.connect(self.server, self.port)

    def download_file(self, file_address: str) -> bool:
        os.chdir(self.data_dir)
        return self.ipfs.get(file_address)

    def upload_file(self, filename: str) -> str:
        os.chdir(self.data_dir)
        res = self.ipfs.add(filename)
        return res['Hash']
