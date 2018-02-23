import json


class WebSocketRequest:

    def __init__(self, method: str):
        self.method = method


class WebSocketStatusResponse:

    def __init__(self,
                 pynode_host: str,
                 ipfs_host: str,
                 pandora_address: str,
                 worker_address: str,
                 pynode_state: str,
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


