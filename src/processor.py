from .broker import Broker
from .ipfs_connector import IPFSConnector
from .nn_loader import *


class Processor(NNListener):
    def __init__(self, broker: Broker):
        self.broker = broker
        self.ipfs_connector = IPFSConnector()
        self.nn_loader = NNLoader()

    def cognite_batch(self, arch: str, model: str, data: str) -> (str, int):
        # TODO: Test and raise exceptions
        self.ipfs_connector.download_file(arch)
        self.ipfs_connector.download_file(model)
        self.ipfs_connector.download_file(data)
        self.nn_loader.load_and_run(arch, model, data, self)
        return 'task0', 0

    def get_time_estimate(self):
        # TODO: Implement
        return 0


class IPFSError (Exception):
    def __init__(self, message: str):
        self.message = message


class ModelInconsistencyError (Exception):
    pass


class DataInconsistencyError (Exception):
    pass

