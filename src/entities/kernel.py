import os
import keras

from manager import Manager
from .entity import Entity
from .dataset import Dataset


class Kernel(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.weights_address = None
        self.model_address = None
        self.model = None

    def init_contract(self):
        if super().init_contract() is not True:
            return False

        try:
            self.model_address = self.json_info['model']
            Manager.get_instance().set_job_kernel_ipfs_address(self.model_address)
            # weights can be empty for training process
            self.weights_address = self.json_info['weights']
            Manager.get_instance().set_job_dataset_ipfs_address(self.weights_address)
        except Exception as ex:
            self.logger.error("Wrong Kernel data file structure:")
            self.logger.error(ex.args)
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
        os.chdir(self.ipfs_api.data_dir)
        with open(self.model_address, "r") as json_file:
            json_model = json_file.read()

        self.model = keras.models.model_from_json(json_model)
        # read model weights if exist
        if self.weights_address:
            self.model.load_weights(self.weights_address)
        return self.model

    def inference_prediction(self, dataset: Dataset):
        self.logger.info('Running prediction model inference...')
        return self.model.predict(dataset.dataset)

    def inference_training(self, dataset: Dataset):
        self.logger.info('Running training model inference...')
        self.model.compile(loss=dataset.loss,
                           optimizer=dataset.optimizer)
        self.model.fit(dataset.train_x_dataset,
                       dataset.train_y_dataset,
                       batch_size=dataset.batch_size,
                       epochs=dataset.epochs,
                       validation_split=dataset.validation_split,
                       shuffle=dataset.shuffle,
                       initial_epoch=dataset.initial_epoch)
        # return model weights after model training
        return self.model


