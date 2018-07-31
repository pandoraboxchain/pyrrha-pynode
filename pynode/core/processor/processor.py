import logging
import h5py
import os

from abc import ABCMeta, abstractmethod
from threading import Thread
from core.processor.entities.kernel import Kernel
from core.processor.entities.dataset import Dataset
from core.manager import Manager
from core.patterns.pynode_logger import LogSocketHandler


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

    def __init__(self, ipfs_api, processor_id: str, delegate: ProcessorDelegate):
        super().__init__()
        # Initializing logger object
        self.logger = logging.getLogger("Processor")
        self.logger.addHandler(LogSocketHandler.get_instance())
        self.manager = Manager.get_instance()
        # Configuring
        self.id = processor_id
        self.results_file = None
        # variables for kernel and dataset objects
        self.kernel = None
        self.kernel_init_result = None
        self.dataset = None
        self.dataset_init_result = None
        # define delegate
        self.ipfs_api = ipfs_api
        self.delegate = delegate
        # root files pth

    def prepare(self, kernel_file, dataset_file, batch: int) -> bool:
        try:
            self.kernel = Kernel(kernel_file=kernel_file,
                                 ipfs_api=self.ipfs_api)
            self.kernel_init_result = self.kernel.init_kernel()
            self.logger.info('Kernel init result : ' + str(self.kernel_init_result))

            self.dataset = Dataset(dataset_file=dataset_file,
                                   ipfs_api=self.ipfs_api,
                                   batch_no=batch)
            self.dataset_init_result = self.dataset.init_dataset()
            self.logger.info('Dataset init result : ' + str(self.dataset_init_result))
        except Exception as ex:
            self.logger.error("Error instantiating cognitive job entities: %s", type(ex))
            self.logger.error(ex.args)
            return False

        if self.kernel_init_result and self.dataset_init_result:
            return True

        self.kernel = None
        self.dataset = None
        return False

    def load(self):
        if self.__load() is False:
            self.delegate.processor_load_failure(processor_id=self.id)
        else:
            self.delegate.processor_load_complete(processor_id=self.id)

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

    def compute(self):
        if self.__load() is False:
            self.delegate.processor_computing_failure(self.id)
            return
        self.logger.info('Current computing mode : ' + self.dataset.process)
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
        self.results_file = str(self.manager.eth_job_id_hex) + '.out.h5'
        try:
            if self.dataset.process == 'predict':
                h5w = h5py.File(self.results_file, 'w')
                h5w.create_dataset('dataset', data=out)
                h5w.close()
            elif self.dataset.process == 'fit':
                out.save_weights(self.results_file)
        except Exception as ex:
            self.logger.error("Error saving results of cognitive work: %s", type(ex))
            self.logger.error(ex.args)
            self.delegate.processor_computing_failure(self.id)
            return
        # need to return file address
        ipfs_result_address = self.ipfs_api.upload_file(self.results_file)
        self.delegate.processor_computing_complete(self.id, ipfs_result_address)
        self.dataset.process = None
        self.clean_up()

    def clean_up(self):
        # clean up files (out file temporary will not be deleted)
        self.logger.info('Clean up data files')
        for filename in os.listdir(os.getcwd()):
            if 'out' not in filename:
                os.remove(filename)
        self.manager.eth_job_id_hex = ''
        self.logger.info('Clean up complete')
