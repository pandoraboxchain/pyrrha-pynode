import logging
from abc import *
from threading import Thread
from ipfs.ipfs_connector import *
from entities.kernel import *
from entities.dataset import *


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
        self.__ipfs_api = IPFSConnector(server=ipfs_server, port=ipfs_port, data_dir=data_dir)
        self.__ipfs_api.connect()

    def prepare(self, kernel: str, dataset: str, batch: int) -> bool:
        try:
            self.kernel = Kernel(address=kernel, abi_path=self.abi_path, abi_file='Kernel', ipfs_api=self.__ipfs_api)
            result = self.kernel.init_contract()
            self.dataset = Dataset(batch_no=batch, address=dataset, abi_path=self.abi_path, abi_file='Dataset', ipfs_api=self.__ipfs_api)
            result &= self.dataset.init_contract()
        except Exception as ex:
            self.logger.error("Error instantiating cognitive job entities: %s", type(ex))
            self.logger.error(ex.args)
            return False
        return result

    def get_time_estimate(self):
        # TODO: Implement
        return 0

    def __load(self) -> bool:
        try:
            self.kernel.read_model()
            self.dataset.read_dataset()
        except Exception as ex:
            self.logger.error("Error reading entities: %s", type(ex))
            self.logger.error(ex.args)
            return False
        return True

    def load(self):
        if self.__load() is False:
            self.delegate.processor_load_failure(self.id)
        else:
            self.delegate.processor_load_complete(self.id)

    def compute(self):
        if self.__load() is False:
            self.delegate.processor_computing_failure(self.id)
            return

        try:
            out = self.kernel.inference(self.dataset)
        except Exception as ex:
            self.logger.error("Error performing neural network inference: %s", type(ex))
            self.logger.error(ex.args)
            self.delegate.processor_computing_failure(self.id)
            return

        self.logger.info('Computing completed successfully, saving results to a file')
        # TODO: Replace with unique string
        self.results_file = 'out.hdf5'

        try:
            h5w = h5py.File(self.results_file, 'w')
            h5w.create_dataset('dataset', data=out)
            self.__ipfs_api.upload_file(self.results_file)
        except Exception as ex:
            self.logger.error("Error saving results of cognitive work: %s", type(ex))
            self.logger.error(ex.args)
            self.delegate.processor_computing_failure(self.id)
            return

        self.delegate.processor_computing_complete(self.id, self.results_file)
