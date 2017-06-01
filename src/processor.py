from ipfs_connector import IPFSConnector, IPFSConfig
from nn_loader import NNListener, NNLoader

class ProcessorCallback:
    pass


class Processor(NNListener):
    def __init__(self, callback: ProcessorCallback, ipfs_config: IPFSConfig):
        print("Connecting to IPFS server %s:%d..." % (ipfs_config.server, ipfs_config.port))
        try:
            self.ipfs_connector = IPFSConnector(ipfs_config)
        except:
            raise IPFSError("Can't connect IPFS server")
        print("IPFS server connected successfully")
        self.nn_loader = NNLoader()

    def cognition_completed(self, results):
        pass

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

