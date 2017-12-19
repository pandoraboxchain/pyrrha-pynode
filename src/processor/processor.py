import keras
import h5py
import numpy as np
import logging

from threading import Thread


class IPFSError (Exception):
    def __init__(self, message: str):
        self.message = message


class ModelInconsistencyError (Exception):
    pass


class DataInconsistencyError (Exception):
    pass


class Processor(Thread):

    def __init__(self, data_dir: str):

        super().__init__()

        # Initializing logger object
        self.logger = logging.getLogger("processor")

        # Configuring
        self.data_dir = data_dir

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

    def load(self, arch: str, weights: str, data: str):
        self.logger.debug('Loading kernel architecture...')
        with open(arch, "r") as json_file:
            json_model = json_file.read()
        model = keras.models.model_from_json(json_model)

        self.logger.debug('Loading kernel weights...')
        model.load_weights(weights)
        h5f = h5py.File(data, 'r')
        # FIX: Magic number for dataset name inside HDF5 file!
        h5ds = h5f['dataset']
        dataset = np.ndarray(shape=h5ds.shape)
        h5ds.read_direct(dest=dataset)
        return model, dataset

    def compute(self, model, dataset):
        self.logger.info('Computing...')
        out = model.predict(dataset)

        self.logger.info('Computing completed successfully, saving results to a file')
        h5w = h5py.File('out.hdf5', 'w')
        h5w.create_dataset('dataset', data=out)
