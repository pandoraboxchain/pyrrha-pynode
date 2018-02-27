
class Manager:
    """
    Manage is global singleton for setting mode variables, global triggers
    Also will be used for saving metrics for perform operative access to
    pynode current states
    """
    # pynode global
    pynode_start_on_launch = None

    # base global eth settings for fast access from any module
    eth_use = None
    eth_host = None
    eth_abi_path = None
    eth_pandora = None
    eth_pandora_contract = None
    eth_worker = None
    eth_worker_contract = None
    eth_cognitive_job_contract = None
    eth_kernel_contract = None
    eth_dataset_contract = None
    # base global ipfs settings for fast access from any module
    ipfs_use = None
    ipfs_storage = None
    ipfs_host = None
    ipfs_port = None
    # base settings for launch tests
    test_host = None

    # launch mode values
    # 0 = SOFT mode (current soft mode without raise exception for normal node work)
    # 1 = HARD mode (strict mode with raises exception for tests, debug and development)
    launch_mode = 0

    # variable for storing global pynode state
    state = 'Online'

    # variable for global storing worker state
    worker_contract_state = None

    # variable for global storing job contract state
    job_contract_state = None

    __instance = None

    def __init__(self):
        if Manager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Manager.__instance = self

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Manager.__instance is None:
            Manager()
        return Manager.__instance

