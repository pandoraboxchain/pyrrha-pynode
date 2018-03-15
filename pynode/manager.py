
class Manager:
    """
    Manage is global singleton for setting mode variables, global triggers
    Also will be used for saving metrics for perform operative access to
    pynode current states
    """

# ----------------------------------
# Global Pynode settings CANT be changed while pynode is launched
# ----------------------------------
    # pynode global
    pynode_start_on_launch = None
    pynode_config_file_path = None
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
    # base settings for web socket launch
    web_socket_enable = False
    web_socket_host = None
    web_socket_port = None
    web_socket_listeners = None
    # base settings for launch tests
    test_host = None

    # launch mode values
    # 0 = SOFT mode (current soft mode without raise exception for normal node work)
    # 1 = HARD mode (strict mode with raises exception for tests, debug and development)
    launch_mode = 0

# ----------------------------------
# Observed variables (change states on pynode process)
# ----------------------------------
    # variable for storing global pynode state
    state = 'Offline'                                       # 'Offline/Online'

    # variable for global storing worker state
    worker_contract_state = 'NotInitialized'                # 'NotInitialized/Initialized'

    # variable for temporary storing job address
    job_contract_address = ''                               # '' - empty or contract address

    # variable for temporary storing job state
    job_contract_state = ''                                 # '' - empty or one of job state

    # variable for temporary storing kernel ipfs address
    job_kernel_ipfs_address = ''                            # '' - empty or address while job is in process

    # variable for temporary storing dataset ipfs address
    job_dataset_ipfs_address = ''                           # '' - empty or address while job is in process

    # variable for storing last result ipfs address
    job_result_ipfs_address = ''                            # '' - empty or address while job is in process

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

# ----------------------------------
# setter methods for observed variables
# ----------------------------------
    def set_state(self, state: str):
        self.state = state
        self.on_property_value_change()

    def set_worker_contract_state(self, state: str):
        if state != self.worker_contract_state:  # avoid duplicates
            self.worker_contract_state = state
            self.on_property_value_change()

    def set_job_contract_address(self, address: str):
        self.job_contract_address = address
        self.on_property_value_change()

    def set_job_contract_state(self, state: str):
        if state != self.job_contract_state:   # avoid duplicates
            self.job_contract_state = state
            self.on_property_value_change()

    def set_job_kernel_ipfs_address(self, address: str):
        self.job_kernel_ipfs_address = address
        self.on_property_value_change()

    def set_job_dataset_ipfs_address(self, address: str):
        self.job_dataset_ipfs_address = address
        self.on_property_value_change()

    def set_job_result_ipfs_address(self, address: str):
        self.job_result_ipfs_address = address
        self.on_property_value_change()

    def set_complete_reset(self):
        self.job_contract_address = ''
        self.job_contract_state = ''
        self.job_kernel_ipfs_address = ''
        self.job_dataset_ipfs_address = ''
        self.on_property_value_change()

# ----------------------------------
# on data or state change event (send complete statuses by socket)
# ----------------------------------
    def on_property_value_change(self):
        if self.web_socket_enable == 'True':
            from webapi.web_socket_listener import WebSocket
            socket = WebSocket.get_instance()
            socket.update_node_status(self)


