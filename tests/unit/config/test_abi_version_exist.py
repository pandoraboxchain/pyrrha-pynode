import unittest
import pynode

from pynode.core.manager import Manager


@unittest.skip("disable for ABI")
class TestABIVersionExist(unittest.TestCase):

    # path for single launch
    # default_ABI_path = '../../../abi/'
    default_ABI_path = 'abi/'

    def test_read_ABI(self):
        try:
            pynode.instantiate_contracts(abi_path=self.default_ABI_path,
                                         eth_hooks='False')
        except Exception as ex:
            print('Default ABI not fount exception')
            print(ex)

        manager = Manager.get_instance()
        assert manager.eth_pandora_contract is not None
        assert manager.eth_worker_contract is not None
        assert manager.eth_cognitive_job_contract is not None
        assert manager.eth_kernel_contract is not None
        assert manager.eth_dataset_contract is not None
