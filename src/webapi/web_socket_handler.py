import json

from manager import Manager
from webapi.web_api_models import WebSocketStatusResponse

"""
Base handler for web socket API
request signature {"method":"status"}
for response we use class json serialization
"""


class WebSocketHandler:
    mode = None
    manager = None

    def __init__(self, mode: int):
        # mode = 0(SOFT) = simple mode with only statistic
        # mode = 1(HARD) = mode with startup and shutdown methods
        self.mode = mode
        # global manager with current data
        self.manager = Manager.get_instance()

    def handle_request(self, data):
        print('request handled : ' + data)
        request = lambda: None
        request.__dict__ = json.loads(data)
        if request.method == 'status':
            return self.__status()
        if request.method == 'startup':
            return self.__startup()
        if request.method == 'shutdown':
            return self.__shutdown()
        return ''

    @staticmethod
    def __startup(self):
        # TODO implement
        return "Not implemented yet"

    @staticmethod
    def __shutdown(self):
        # TODO implement
        return "Not implemented yet"

    def __status(self):
        response = WebSocketStatusResponse(pynode_host=self.manager.eth_host,
                                           ipfs_host=self.manager.ipfs_host+':'+self.manager.ipfs_port,
                                           pandora_address=self.manager.eth_pandora,
                                           worker_address=self.manager.eth_worker,
                                           pynode_state=self.manager.state,
                                           worker_state=self.manager.worker_contract_state)
        return response.serialize()


