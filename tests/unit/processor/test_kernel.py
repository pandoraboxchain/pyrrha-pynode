import unittest
import json
import os

from pynode.core.processor.entities.kernel import Kernel, Dataset
from pynode.integration.ipfs_service import IpfsService
from pynode.integration.dummy.ipfs_connector import IpfsConnectorDummy


class TestKernel(unittest.TestCase):

    # test_kernel_1 - simple kernel file with model only
    # test_kernel_2 - file with model and weigths
    # test_kernel_3 - wrong file

    test_ipfs_instance = None
    test_kernels_path = '../tests/data/test_kernel_'
    kernel_1_file = None
    kernel_2_file = None
    kernel_3_file = None

    @classmethod
    def setUpClass(cls):
        cls.test_ipfs_instance = IpfsService(strategic=IpfsConnectorDummy())
        if 'travis' in os.getcwd():  # fix path for travis launch
            cls.test_kernels_path = 'tests/data/test_kernel_'

        with open(cls.test_kernels_path+'1') as json_file:
            cls.kernel_1_file = json.load(json_file)
        with open(cls.test_kernels_path+'2') as json_file:
            cls.kernel_2_file = json.load(json_file)
        with open(cls.test_kernels_path+'3') as json_file:
            cls.kernel_3_file = json.load(json_file)

    # ------------------------------------
    # kernel init testing
    # here need to check all possibilities for False init result

    def test_init_kernel(self):
        kernel = Kernel(kernel_file=self.kernel_1_file,
                        ipfs_api=self.test_ipfs_instance)
        assert kernel.init_kernel() is True
        assert kernel.model_address is not None
        assert kernel.weights_address is ''

    def test_init_kernel_with_weights(self):
        kernel = Kernel(kernel_file=self.kernel_2_file,
                        ipfs_api=self.test_ipfs_instance)
        assert kernel.init_kernel() is True
        assert kernel.model_address is not None
        assert kernel.weights_address is not None

    def test_init_kernel_with_wrong_kernel_file(self):
        kernel = Kernel(kernel_file=self.kernel_3_file,
                        ipfs_api=self.test_ipfs_instance)
        assert kernel.init_kernel() is False
        assert kernel.model_address is None
        assert kernel.weights_address is None

    # ----------------------------------
    # tests for reading model

    # normal model
    def test_read_model(self):
        kernel = Kernel(kernel_file=self.kernel_1_file,
                        ipfs_api=self.test_ipfs_instance)
        if 'travis' in os.getcwd():  # fix path for travis launch
            kernel.model_address = 'tests/data/test_model_1'
        else:
            kernel.model_address = '../tests/data/test_model_1'
        result = kernel.read_model()
        assert result is not None

    # wrong saved model
    def test_read_wrong_model(self):
        kernel = Kernel(kernel_file=self.kernel_1_file,
                        ipfs_api=self.test_ipfs_instance)
        if 'travis' in os.getcwd():  # fix path for travis launch
            kernel.model_address = 'tests/data/test_model_2'
        else:
            kernel.model_address = '../tests/data/test_model_2'
        result = kernel.read_model()
        assert result is None

    # model with invalid json
    def test_read_wrong_model_json(self):
        kernel = Kernel(kernel_file=self.kernel_1_file,
                        ipfs_api=self.test_ipfs_instance)
        if 'travis' in os.getcwd():  # fix path for travis launch
            kernel.model_address = 'tests/data/test_model_3'
        else:
            kernel.model_address = '../tests/data/test_model_3'
        result = kernel.read_model()
        assert result is None
