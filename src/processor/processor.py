import h5py
import logging
from abc import *
from threading import Thread
from ipfs.ipfs_connector import *
from entities.kernel import Kernel
from entities.dataset import Dataset


class IPFSError (Exception):
    def __init__(self, message: str):
        self.message = message


class ModelInconsistencyError (Exception):
    pass


class DataInconsistencyError (Exception):
    pass


class ProcessorDelegate(metaclass=ABCMeta):
    @abstractmethod
    def processor_load_complete(self, processor_id: str):
        pass

    @abstractmethod
    def processor_load_failure(self, processor_id: str):
        pass

    @abstractmethod
    def processor_computing_complete(self, processor_id: str, results_file: str):
        pass

    @abstractmethod
    def processor_computing_failure(self, processor_id: str):
        pass


class Processor(Thread):

    def __init__(self, id: str, ipfs_server: str, ipfs_port: int, data_dir: str, abi_path: str, delegate: ProcessorDelegate):

        super().__init__()

        # Initializing logger object
        self.logger = logging.getLogger("Processor")

        # Configuring
        self.id = id
        self.data_dir = data_dir
        self.abi_path = abi_path
        self.results_file = None
        self.kernel = None
        self.dataset = None
        self.delegate = delegate

        # Initializing IPFS
        self.ipfs = IPFSConnector(server=ipfs_server, port=ipfs_port, data_dir=data_dir)

    def prepare(self, kernel: str, dataset: str, batch: int) -> bool:
        try:
            self.kernel = Kernel(kernel, self.abi_path, 'Kernel', self.ipfs)
            result = self.kernel.init_contract()
            self.dataset = Dataset(batch, dataset, self.abi_path, 'Dataset')
            result &= self.dataset.init_contract()
        except:
            return False
        return result

    def get_time_estimate(self):
        # TODO: Implement
        return 0

    def load(self):
        self.kernel.read_model()
        self.dataset.read_dataset()
        self.delegate.processor_load_complete(self.id)

    def compute(self, model, dataset):
        self.load()

        self.logger.info('Computing...')
        out = model.predict(dataset)

        self.logger.info('Computing completed successfully, saving results to a file')
        # TODO: Replace with unique string
        self.results_file = 'out.hdf5'
        h5w = h5py.File(self.results_file, 'w')
        h5w.create_dataset('dataset', data=out)
        self.delegate.processor_computing_complete(self.id, self.results_file)
