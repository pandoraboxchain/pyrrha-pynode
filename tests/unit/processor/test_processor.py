import unittest
import json
import os

from pynode.core.processor.processor import Processor, ProcessorDelegate
from pynode.integration.ipfs_service import IpfsService
from pynode.integration.dummy.ipfs_connector import IpfsConnectorDummy


class TestProcessor(unittest.TestCase, ProcessorDelegate):

    # test_kernel_1 - simple kernel file with model only
    # test_kernel_2 - file with model and weigths
    # test_kernel_3 - wrong file
    # test_dataset_1.json - simple dataset for training
    # test_dataset_2.json - file for prediction
    # test_dataset_3.json - wrong file (without train_y field)

    test_ipfs_instance = None

    test_kernels_path = '../tests/data/test_kernel_'
    kernel_1_file = None
    kernel_2_file = None
    kernel_3_file = None

    test_dataset_path = '../tests/data/test_dataset_'
    dataset_1_file = None
    dataset_2_file = None
    dataset_3_file = None

    @classmethod
    def setUpClass(cls):
        cls.test_ipfs_instance = IpfsService(strategic=IpfsConnectorDummy())
        if 'travis' in os.getcwd():  # fix path for travis launch
            cls.test_kernels_path = 'tests/data/test_kernel_'

        with open(cls.test_kernels_path + '1') as json_file:
            cls.kernel_1_file = json.load(json_file)
        with open(cls.test_kernels_path + '2') as json_file:
            cls.kernel_2_file = json.load(json_file)
        with open(cls.test_kernels_path + '3') as json_file:
            cls.kernel_3_file = json.load(json_file)

        if 'travis' in os.getcwd():  # fix path for travis launch
            cls.test_dataset_path = 'tests/data/test_dataset_'

        with open(cls.test_dataset_path + '1.json') as json_file:
            cls.dataset_1_file = json.load(json_file)
        with open(cls.test_dataset_path + '2.json') as json_file:
            cls.dataset_2_file = json.load(json_file)
        with open(cls.test_dataset_path + '3.json') as json_file:
            cls.dataset_3_file = json.load(json_file)

    # ------------------------------------
    # test init processor
    def test_init_processor_for_fit(self):
        processor = Processor(ipfs_api=self.test_ipfs_instance,
                              processor_id=0,
                              delegate=self)
        processor_prepare_result = processor.prepare(kernel_file=self.kernel_1_file,
                                                     dataset_file=self.dataset_1_file,
                                                     batch=0)
        assert processor_prepare_result is True
        assert processor.kernel is not None
        assert processor.dataset is not None
        assert processor.dataset.process == 'fit'
        # training necessary params
        assert processor.dataset.train_x_address == 'QmQNWiv1s7rhoUrfELCtK65VZGbTE79Bfa3kkoeFf7aVQA'
        assert processor.dataset.train_y_address == 'QmT3keTG7fXrPRZApjwVWvZDamLC5LeyvQLou4rSJLJJEj'
        assert processor.dataset.loss == 'categorical_crossentropy'
        assert processor.dataset.optimizer == 'adam'
        assert processor.dataset.batch_size == 128
        assert processor.dataset.epochs == 10
        assert processor.dataset.validation_split == 0.1
        assert processor.dataset.shuffle == 'False'
        assert processor.dataset.initial_epoch == 0

    def test_init_processor_for_predict(self):
        processor = Processor(ipfs_api=self.test_ipfs_instance,
                              processor_id=0,
                              delegate=self)
        processor_prepare_result = processor.prepare(kernel_file=self.kernel_2_file,
                                                     dataset_file=self.dataset_2_file,
                                                     batch=0)
        assert processor_prepare_result is True
        assert processor.kernel is not None
        assert processor.dataset is not None
        assert processor.dataset.process == 'predict'
        # prediction necessary params
        assert processor.dataset.init_dataset() is True
        assert processor.dataset.train_x_address == ''
        assert processor.dataset.train_y_address == ''
        assert processor.dataset.loss == ''
        assert processor.dataset.optimizer == ''
        assert processor.dataset.batch_size == 0
        assert processor.dataset.epochs == 0
        assert processor.dataset.validation_split == 0
        assert processor.dataset.shuffle == ''
        assert processor.dataset.initial_epoch == 0

    def test_init_processor_kernel_error(self):
        processor = Processor(ipfs_api=self.test_ipfs_instance,
                              processor_id=0,
                              delegate=self)
        processor_prepare_result = processor.prepare(kernel_file=self.kernel_3_file,
                                                     dataset_file=self.dataset_2_file,
                                                     batch=0)
        assert processor_prepare_result is False
        assert processor.kernel is None
        assert processor.dataset is None

    def test_init_processor_dataset_predict(self):
        processor = Processor(ipfs_api=self.test_ipfs_instance,
                              processor_id=0,
                              delegate=self)
        processor_prepare_result = processor.prepare(kernel_file=self.kernel_1_file,
                                                     dataset_file=self.dataset_3_file,
                                                     batch=0)
        assert processor_prepare_result is True

    # ------------------------------------
    # test load processor
    def test_processor_load(self):
        processor = Processor(ipfs_api=self.test_ipfs_instance,
                              processor_id=0,
                              delegate=self)
        processor.prepare(kernel_file=self.kernel_1_file,
                          dataset_file=self.dataset_1_file,
                          batch=0)
        if 'travis' in os.getcwd():
            # path for Travis launch
            processor.kernel.model_address = 'tests/data/test_model_1'
            # take fake files for test passing
            processor.dataset.train_x_address = 'tests/data/test_train_x.h5'
            processor.dataset.train_y_address = 'tests/data/test_train_y.h5'
        else:
            # path for Travis launch
            processor.kernel.model_address = '../tests/data/test_model_1'
            # take fake files for test passing
            processor.dataset.train_x_address = '../tests/data/test_train_x.h5'
            processor.dataset.train_y_address = '../tests/data/test_train_y.h5'

        processor.load()  # result of loading returns to callback

    def test_processor_load_fail(self):
        processor = Processor(ipfs_api=self.test_ipfs_instance,
                              processor_id=1,
                              delegate=self)
        processor.prepare(kernel_file=self.kernel_1_file,
                          dataset_file=self.dataset_1_file,
                          batch=0)
        if 'travis' in os.getcwd():
            processor.kernel.model_address = 'tests/data/test_model_1'
        else:
            processor.kernel.model_address = '../tests/data/test_model_1'
        processor.load()

    # ------------------------------------
    # test processor delegate
    # ------------------------------------
    def processor_load_complete(self, processor_id: str):
        assert processor_id is 0

    def processor_load_failure(self, processor_id: str):
        assert processor_id is 1

    def processor_computing_complete(self, processor_id: str, results_file: str):
        pass

    def processor_computing_failure(self, processor_id: str):
        pass