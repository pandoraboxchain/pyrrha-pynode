from ipfs_connector import IPFSConnector
from nn_loader import *


class ProcessorCallback:
    pass


class Processor(NNListener):
    def __init__(self, callback: ProcessorCallback):
        print("Connecting to IPFS...")
        self.ipfs_connector = IPFSConnector()
        print("IPFS connected successfully.")
        self.nn_loader = NNLoader()

    def cognite_batch(self, arch: str, model: str, data: str) -> (str, int):
        try:
            print("Downloading architecture file %s" % arch)
            self.ipfs_connector.download_file(arch)
        except:
            raise IPFSError("Architecture file not found")

        try:
            print("Downloading model file %s" % model)
            self.ipfs_connector.download_file(model)
        except:
            raise IPFSError("Model file not found")

        try:
            print("Downloading data file %s" % data)
            self.ipfs_connector.download_file(data)
        except:
            raise IPFSError("Data file not found")

        print("Running model and data..")
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

