from abc import ABCMeta, abstractmethod

import keras
import logging

from core.patterns.pynode_logger import LogSocketHandler
from core.manager import Manager
from .dataset import Dataset


class ProgressDelegate(metaclass=ABCMeta):
    @abstractmethod
    def on_train_begin(self, logs={}):
        pass

    @abstractmethod
    def on_train_end(self, logs={}):
        pass

    @abstractmethod
    def on_epoch_begin(self, epoch, epochs, logs={}):
        pass

    @abstractmethod
    def on_epoch_end(self, epoch, epochs, logs={}):
        pass


class ProgressCallback(keras.callbacks.Callback):
    def __init__(self, delegate: ProgressDelegate, epochs: int):
        self.delegate = delegate
        self.total_epochs = epochs

    def on_train_begin(self, logs={}):
        self.delegate.on_train_begin(logs=logs)

    def on_train_end(self, logs={}):
        self.delegate.on_train_end(logs=logs)

    def on_epoch_begin(self, epoch, logs={}):
        self.delegate.on_epoch_begin(epoch=epoch,
                                     epochs=self.total_epochs,
                                     logs=logs)

    def on_epoch_end(self, epoch, logs={}):
        self.delegate.on_epoch_end(epoch=epoch,
                                   epochs=self.total_epochs,
                                   logs=logs)


class Kernel:

    def __init__(self, kernel_file, ipfs_api, delegate: ProgressDelegate):
        # Initializing logger object
        self.logger = logging.getLogger("Kernel")
        self.logger.addHandler(LogSocketHandler.get_instance())
        self.manager = Manager.get_instance()

        self.json_kernel = kernel_file
        self.ipfs_api = ipfs_api
        self.model_address = None
        self.weights_address = None
        self.model = None

        self.progress_delegate = delegate

    def init_kernel(self):
        # get main kernel params
        try:
            self.model_address = self.json_kernel['model']
            Manager.get_instance().set_job_kernel_ipfs_address(self.model_address)
            self.weights_address = self.json_kernel['weights']
            Manager.get_instance().set_job_dataset_ipfs_address(self.weights_address)
        except Exception as ex:
            self.logger.error("Wrong Kernel data file structure:")
            self.logger.error(ex.args)
            return False

        # ------------------------------
        # validate values by string type
        # ------------------------------
        # model address is necessary
        if not isinstance(self.model_address, str):
            self.logger.error("Wrong model address type : " + str(type(self.model_address)))
            self.model_address = None
            self.weights_address = None
            return False
        # weights is not necessary and may be empty
        if self.weights_address is not None:
            if not isinstance(self.weights_address, str):
                self.logger.error("Wrong weights address type : " + str(type(self.weights_address)))
                self.weights_address = None
                return False

        try:
            self.logger.info("Downloading model file %s", self.model_address)
            self.ipfs_api.download_file(self.model_address)
            if self.weights_address:
                self.logger.info("Downloading weights file %s", self.weights_address)
                self.ipfs_api.download_file(self.weights_address)
            else:
                self.logger.info("Weights address is empty, skip downloading")
        except Exception as ex:
            self.logger.error("Can't download kernel files from IPFS: %s", type(ex))
            self.logger.error(ex.args)
            return False

        return True

    def read_model(self) -> str:
        if self.model is not None:
            return self.model
        self.logger.info('Loading kernel architecture...')
        with open(self.model_address, "r") as json_file:
            json_model = json_file.read()

        try:
            self.model = keras.models.model_from_json(json_model)
        except Exception as ex:
            self.logger.error('Error reading kernel model')
            self.logger.error(ex.args)
            return None
        return self.model

    def inference_prediction(self, dataset: Dataset):
        self.logger.info('Running prediction model inference...')
        self.model.compile(loss=dataset.loss,
                           optimizer=dataset.optimizer)
        # check and load weights after model compile
        if self.weights_address:
            if self.weights_address != self.model_address:
                self.model.load_weights(self.weights_address)
        result = self.model.predict(dataset.dataset, batch_size=100)  # may be take from price ? (100 for test)
        # tensorflow bug https://github.com/tensorflow/tensorflow/issues/14356
        keras.backend.clear_session()
        return result

    def inference_training(self, dataset: Dataset):
        self.logger.info('Running training model inference...')
        self.model.compile(loss=dataset.loss,
                           optimizer=dataset.optimizer)
        callback_handler = ProgressCallback(self.progress_delegate, dataset.epochs)
        self.model.fit(dataset.train_x_dataset,
                       dataset.train_y_dataset,
                       batch_size=dataset.batch_size,
                       epochs=dataset.epochs,
                       validation_split=dataset.validation_split,
                       shuffle=dataset.shuffle,
                       initial_epoch=dataset.initial_epoch,
                       callbacks=[callback_handler])
        # return model weights after model training
        return self.model


