import os
import keras
from .entity import Entity


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
            self.model_address = self.__info['model']
            self.weights_address = self.__info['weights']
        except:
            self.logger.error("Wrong Kernel data file structure")
            return False

        try:
            self.logger.info("Downloading model file %s", self.model_address)
            self.__ipfs_api.download_file(self.model_address)
            self.logger.info("Downloading weights file %s", self.weights_address)
            self.__ipfs_api.download_file(self.weights_address)
        except:
            self.logger.error("Can't download kernel files from IPFS")
            return False

        return True

    def read_model(self) -> str:
        if self.model is not None:
            return self.model

        self.logger.info('Loading kernel architecture...')
        os.chdir(self.__ipfs_api.data_dir)
        with open(self.model_address, "r") as json_file:
            json_model = json_file.read()

        self.model = keras.models.model_from_json(json_model)
        self.model.load_weights(self.weights_address)

        return self.model
