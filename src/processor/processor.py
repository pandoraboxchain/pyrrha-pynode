import logging
from abc import *
from threading import Thread
from ipfs.ipfs_connector import *
from entities.kernel import *
from entities.dataset import *
from manager import Manager
from patterns.pynode_logger import LogSocketHandler


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

    def __init__(self, processor_id: str, ipfs_server: str, ipfs_port: int,
                 data_dir: str, abi_path: str, delegate: ProcessorDelegate):

        super().__init__()

        # Initializing logger object
        self.logger = logging.getLogger("Processor")
        self.logger.addHandler(LogSocketHandler.get_instance())
        self.manager = Manager.get_instance()

        # Configuring
        self.id = processor_id
        self.data_dir = data_dir
        self.abi_path = abi_path
        # result variable
        self.results_file = None

        # variables for kernel and dataset objects
        self.kernel = None
        self.dataset = None

        # define delegate
        self.delegate = delegate

        # Initializing IPFS
        self.__ipfs_api = IPFSConnector(server=ipfs_server,
                                        port=ipfs_port,
                                        data_dir=data_dir)
        self.__ipfs_api.connect()

    def prepare(self, kernel: str, dataset: str, batch: int) -> bool:
        try:
            self.kernel = Kernel(address=kernel,
                                 contract=self.manager.eth_kernel_contract,
                                 ipfs_api=self.__ipfs_api)
            result = self.kernel.init_contract()

            self.dataset = Dataset(batch_no=batch,
                                   address=dataset,
                                   contract=self.manager.eth_dataset_contract,
                                   ipfs_api=self.__ipfs_api)
            result &= self.dataset.init_contract()
        except Exception as ex:
            self.logger.error("Error instantiating cognitive job entities: %s", type(ex))
            self.logger.error(ex.args)
            return False
        return result

    @staticmethod
    def get_time_estimate():
        # TODO: Implement
        return 0

    def __load(self) -> bool:
        # load data sets for computing
        try:
            # reading kernel data
            self.kernel.read_model()
            # prepare data for prediction or training
            if self.dataset.process == 'predict':
                self.dataset.read_dataset()
            elif self.dataset.process == 'fit':
                self.dataset.read_x_train_dataset()
                self.dataset.read_y_train_dataset()
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
            if self.dataset.process == 'predict':
                # return prediction result
                out = self.kernel.inference_prediction(self.dataset)
            elif self.dataset.process == 'fit':
                # return model instance after training
                out = self.kernel.inference_training(self.dataset)
        except Exception as ex:
            self.logger.error("Error performing neural network inference: %s", type(ex))
            self.logger.error(ex.args)
            self.delegate.processor_computing_failure(self.id)
            return

        self.logger.info('Computing completed successfully, saving results to a file')
        self.commit_computing_result(out)

    def commit_computing_result(self, out):
        self.results_file = str(self.manager.job_contract_address) + '.out.hdf5'
        try:
            if self.dataset.process == 'predict':
                h5w = h5py.File(self.results_file, 'w')
                h5w.create_dataset('dataset', data=out)
            elif self.dataset.process == 'fit':
                out.save_weights(self.results_file)
        except Exception as ex:
            self.logger.error("Error saving results of cognitive work: %s", type(ex))
            self.logger.error(ex.args)
            self.delegate.processor_computing_failure(self.id)
            return
        self.__ipfs_api.upload_file(self.results_file)
        self.delegate.processor_computing_complete(self.id, self.results_file)


