import json


class WebSocketRequest:

    def __init__(self, method: str):
        self.method = method


# pynode settings model for get and set settings to pynode
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
                      # config file server path
                      pynode_config_file_path: str,
                      # launch mode for pynode
                      pynode_launch_mode: int,
                      # launch mode from config file to use
                      ethereum_connection_use: str,
                      # connection host used
                      ethereum_connection_host: str,
                      # ipfs connection config to use
                      ipfs_connection_use: str,
                      # ipfs connection host to use
                      ipfs_connection_host: str,
                      # pandora contract address
                      pandora_contract_address: str,
                      # worker contract address
                      worker_contract_address: str
                      ):
        self.pynode_config_file_path = pynode_config_file_path
        self.pynode_launch_mode = pynode_launch_mode
        self.ethereum_connection_use = ethereum_connection_use
        self.ethereum_connection_host = ethereum_connection_host
        self.ipfs_connection_use = ipfs_connection_use
        self.ipfs_connection_host = ipfs_connection_host
        self.pandora_contract_address = pandora_contract_address
        self.worker_contract_address = worker_contract_address

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)

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


class PynodeStatus:
    def __init__(self,
                 # pynode host address
                 pynode_host: str,
                 # ipfs host address
                 ipfs_host: str,
                 # pandora contract address
                 pandora_address: str,
                 # worker contract address
                 worker_address: str,
                 # pynode state
                 pynode_state: str,
                 # worker state
                 worker_state: str):
        self.pynode_host = pynode_host
        self.ipfs_host = ipfs_host
        self.pandora_address = pandora_address
        self.worker_address = worker_address
        self.pynode_status = pynode_state
        self.worker_status = worker_state

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)

