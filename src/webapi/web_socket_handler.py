import json
import webapi
import time
import sys
import pynode
import logging

from manager import Manager
from webapi.web_api_models import *


"""
Base handler for web socket API
request signature {"method":"get_status"}
for response we use class json serialization
"""


class WebSocketHandler:
    mode = None
    manager = None
    listener = None
    clients = None

    def __init__(self, listener):
        self.manager = Manager.get_instance()
        self.mode = self.manager.launch_mode
        self.listener = listener

    @staticmethod
    def get_instance():
        return WebSocketHandler.__instance

    def handle_request(self, data):
        print('request handled : ' + data)
        request = lambda: None
        request.__dict__ = json.loads(data)
        if request.method == 'get_settings':
            return self.get_current_settings()
#        if request.method == 'set_settings':
#            return self.set_current_settings(data)
        if request.method == 'startup':
            return pynode.run_pynode()
#        if request.method == 'get_status':
#            return self.get_status()
        return ''

    def get_current_settings(self):
        # return settings from manager
        response = PynodeSettings()
        response.define_object(pynode_config_file_path=self.manager.eth_abi_path,
                               pynode_launch_mode=self.manager.launch_mode,
                               ethereum_connection_use=self.manager.eth_use,
                               ethereum_connection_host=self.manager.eth_host,
                               ipfs_connection_use=self.manager.ipfs_use,
                               ipfs_connection_host=self.manager.ipfs_host+":"+self.manager.ipfs_port,
                               pandora_contract_address=self.manager.eth_pandora,
                               worker_contract_address=self.manager.eth_worker)
        return response.serialize()

    def set_current_settings(self, data):
        request = PynodeSettings()
        request = request.deserialize(data)
        # not all data is enable for change
        # possible to change :
        # launch_mode, eth_node host, ipfs host,
        # pandora contract address, worker contract address
        if request.pynode_launch_mode:
            self.manager.launch_mode = request.pynode_launch_mode
        if request.ethereum_connection_host:
            self.manager.eth_host = request.ethereum_connection_host
        if request.ipfs_connection_host:
            self.manager.ipfs_host = request.ipfs_connection_host
        if request.pandora_contract_address:
            self.manager.eth_pandora = request.pandora_contract_address
        if request.worker_contract_address:
            self.manager.eth_worker = request.worker_contract_address
        return self.get_current_settings()

    def get_status(self):
        # return current status from manager
        response = PynodeStatus(pynode_host=self.manager.eth_host,
                                ipfs_host=self.manager.ipfs_host + ':' + self.manager.ipfs_port,
                                pandora_address=self.manager.eth_pandora,
                                worker_address=self.manager.eth_worker,
                                pynode_state=self.manager.state,
                                worker_state=self.manager.worker_contract_state)
        return response.serialize()


