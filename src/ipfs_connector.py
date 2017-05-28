import ipfsapi


class IPFSConnector:

    def __init__(self):
        self.api = ipfsapi.connect('127.0.0.1', 5001)
        pass
