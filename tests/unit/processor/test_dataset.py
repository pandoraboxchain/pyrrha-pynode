import unittest
import json
import os

from pynode.core.processor.entities.kernel import Kernel, Dataset
from pynode.integration.ipfs_service import IpfsService
from pynode.integration.dummy.ipfs_connector import IpfsConnectorDummy


class TestDataset(unittest.TestCase):

    # test_dataset_1.json - simple dataset for training
    # test_dataset_2.json - file for prediction
    # test_dataset_3.json - wrong file (without train_y field)

    test_ipfs_instance = None

    test_dataset_path = '../tests/data/test_dataset_'
    dataset_1_file = None
    dataset_2_file = None
    dataset_3_file = None

    @classmethod
    def setUpClass(cls):
        cls.test_ipfs_instance = IpfsService(strategic=IpfsConnectorDummy())
        if 'travis' in os.getcwd():  # fix path for travis launch
            cls.test_dataset_path = 'tests/data/test_dataset_'

        with open(cls.test_dataset_path + '1.json') as json_file:
            cls.dataset_1_file = json.load(json_file)
        with open(cls.test_dataset_path + '2.json') as json_file:
            cls.dataset_2_file = json.load(json_file)
        with open(cls.test_dataset_path + '3.json') as json_file:
            cls.dataset_3_file = json.load(json_file)

    # ------------------------------------
    # dataset init testing
    # here need to check all possibilities for False init result

    def test_init_dataset(self):
        dataset = Dataset(dataset_file=self.dataset_1_file,
                          ipfs_api=self.test_ipfs_instance,
                          batch_no=0)
        assert dataset.init_dataset() is True
        assert dataset.train_x_address == 'QmQNWiv1s7rhoUrfELCtK65VZGbTE79Bfa3kkoeFf7aVQA'
        assert dataset.train_y_address == 'QmT3keTG7fXrPRZApjwVWvZDamLC5LeyvQLou4rSJLJJEj'
        assert dataset.loss == 'categorical_crossentropy'
        assert dataset.optimizer == 'adam'
        assert dataset.batch_size == 128
        assert dataset.epochs == 10
        assert dataset.validation_split == 0.1
        assert dataset.shuffle == 'False'
        assert dataset.initial_epoch == 0
        # data in dataset is for fit operation
        assert dataset.process == 'fit'

    def test_init_dataset_for_prediction(self):
        dataset = Dataset(dataset_file=self.dataset_2_file,
                          ipfs_api=self.test_ipfs_instance,
                          batch_no=0)
        assert dataset.init_dataset() is True
        assert dataset.train_x_address is None
        assert dataset.train_y_address is None
        assert dataset.loss == 'categorical_crossentropy'
        assert dataset.optimizer == 'adam'
        assert dataset.batch_size is None
        assert dataset.epochs is None
        assert dataset.validation_split == 0
        assert dataset.shuffle is False
        assert dataset.initial_epoch == 0
        # data in dataset is for fit operation
        assert dataset.process == 'predict'

    def test_fail_init_dataset(self):
        dataset = Dataset(dataset_file=self.dataset_3_file,
                          ipfs_api=self.test_ipfs_instance,
                          batch_no=0)
        assert dataset.init_dataset() is True  # inference predict strategy
