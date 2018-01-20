import os
import h5py
import numpy as np
from .entity import Entity


class Dataset(Entity):

    def __init__(self, batch_no: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_address = None
        self.batch_no = batch_no
        self.dataset = None

    def init_contract(self):
        if super().init_contract() is not True:
            return False

        try:
            batches = self.json_info['batches']
            self.data_address = batches[self.batch_no]
        except Exception as ex:
            self.logger.error("Wrong Dataset data file structure")
            self.logger.error(ex.args)
            return False

        try:
            self.logger.info("Downloading data file %s", self.data_address)
            self.ipfs_api.download_file(self.data_address)
        except Exception as ex:
            self.logger.error("Can't download data file from IPFS: %s", type(ex))
            self.logger.error(ex.args)
            return False

        return True

    def read_dataset(self) -> np.ndarray:
        if self.dataset is not None:
            return self.dataset

        self.logger.info('Loading dataset...')
        os.chdir(self.ipfs_api.data_dir)
        h5f = h5py.File(self.data_address, 'r')
        # FIX: Magic number for dataset name inside HDF5 file!
        h5ds = h5f['dataset']
        self.dataset = np.ndarray(shape=h5ds.shape)
        h5ds.read_direct(dest=self.dataset)
        return self.dataset
