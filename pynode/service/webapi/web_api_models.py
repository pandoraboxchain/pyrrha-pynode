import json


# ---------------------------------
# base serializer class
# ---------------------------------
class ClassApiSerializer:

    object_type = None
    data = None

    def serialize(self, inner_object):
        self.object_type = inner_object.__class__.__name__
        self.data = inner_object
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    # deserialize will be used on change settings
    def deserialize(self, json_object):
        self.__dict__ = json.loads(json_object)
        try:
            pynode_settings = self.__dict__['pynode_settings']
            for key in pynode_settings:
                for field in self.__dict__['pynode_settings']:
                    if key == field:
                        self.__dict__[field] = pynode_settings[key]
            return self
        except Exception as ex:
            print(ex)


# ---------------------------------
# model for request (will be updated)
# ---------------------------------
class WebSocketRequest:
    def __init__(self, method: str):
        self.method = method


# ---------------------------------
# model for get/set pynode settings
# ---------------------------------
class PynodeSettings:
    pynode_config_file_path = None   # only read
    pynode_launch_mode = None        # get/set
    ethereum_connection_use = None   # only read
    ethereum_connection_host = None  # get/set
    ipfs_connection_use = None       # only read
    ipfs_connection_host = None      # get/set
    pandora_contract_address = None  # get/set
    worker_contract_address = None   # get/set

    def define_object(self,
                      pynode_config_file_path: str,
                      pynode_launch_mode: int,
                      ethereum_connection_use: str,
                      ethereum_connection_host: str,
                      ipfs_connection_use: str,
                      ipfs_connection_host: str,
                      pandora_contract_address: str,
                      worker_contract_address: str):
        self.pynode_config_file_path = pynode_config_file_path
        self.pynode_launch_mode = pynode_launch_mode
        self.ethereum_connection_use = ethereum_connection_use
        self.ethereum_connection_host = ethereum_connection_host
        self.ipfs_connection_use = ipfs_connection_use
        self.ipfs_connection_host = ipfs_connection_host
        self.pandora_contract_address = pandora_contract_address
        self.worker_contract_address = worker_contract_address


# ---------------------------------
# model for sending pynode log messages
# ---------------------------------
class PynodeLogRecord:
    process_name = None
    level_name = None
    file_name = None
    module = None
    message = None

    def define_object(self,
                      process_name: str,
                      level_name: str,
                      file_name: str,
                      module: str,
                      message: str):
        self.process_name = process_name
        self.level_name = level_name
        self.file_name = file_name
        self.module = module
        self.message = message


# ---------------------------------
# model for sending pynode status
# ---------------------------------
class PynodeStatus:
    # global pynode state (Online, Offline)
    state = None
    # -----------------------
    # for information updates
    ethereum_host = None
    ipfs_host = None
    pandora_address = None
    worker_address = None
    # -----------------------
    # pynode statuses
    # current worker contract status
    worker_status = None
    # current job contract address if job exist
    job_address = None
    # current job contract status if job exist
    job_status = None
    # if job exist get its kernel address
    kernel_address = None
    # if job exist get its dataset address
    dataset_address = None
    # ipfs result address from last job
    job_result_address = None

    def define_object(self,
                      state: str,
                      ethereum_host: str,
                      ipfs_host: str,
                      pandora_address: str,
                      worker_address: str,

                      worker_state: str,
                      job_address: str,
                      job_status: str,
                      kernel_address: str,
                      dataset_address: str,
                      job_result_address: str):
        self.state = state
        self.ethereum_host = ethereum_host
        self.ipfs_host = ipfs_host
        self.pandora_address = pandora_address
        self.worker_address = worker_address
        self.worker_status = worker_state
        self.job_address = job_address
        self.job_status = job_status
        self.kernel_address = kernel_address
        self.dataset_address = dataset_address
        self.job_result_address = job_result_address


