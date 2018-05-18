import unittest
import json

from pynode.service.webapi.web_api_models import ClassApiSerializer, PynodeSettings, PynodeStatus


class TestWebApi(unittest.TestCase):

    def test_model_for_settings(self):
        settings = PynodeSettings()
        settings.define_object(pynode_config_file_path='../abi/',
                               pynode_launch_mode=0,
                               ethereum_connection_use='remote',
                               ethereum_connection_host='http://rinkeby.pandora.network:8545',
                               ipfs_connection_use='pandora',
                               ipfs_connection_host='http://ipfs.pandora.network',
                               pandora_contract_address='0x9f301cfd1217fd60e4244a12b1edffe458e8b9bd',
                               worker_contract_address='0x6ac66706c9eF0b2A6eD6B471fb2d086d0C7BC055')
        serialized_settings = str.encode(ClassApiSerializer().serialize(settings))
        serialized_object = json.loads(serialized_settings)
        json_object = json.loads("""
        {"data":
            {"ethereum_connection_host": "http://rinkeby.pandora.network:8545",
             "ethereum_connection_use": "remote",
             "ipfs_connection_host": "http://ipfs.pandora.network",
             "ipfs_connection_use": "pandora",
             "pandora_contract_address": "0x9f301cfd1217fd60e4244a12b1edffe458e8b9bd",
             "pynode_config_file_path": "../abi/",
             "pynode_launch_mode": 0,
             "worker_contract_address": "0x6ac66706c9eF0b2A6eD6B471fb2d086d0C7BC055"
            },
            "object_type": "PynodeSettings"
        }""")

        assert serialized_object['data']['ethereum_connection_host'] == json_object['data']['ethereum_connection_host']
        assert serialized_object['data']['ethereum_connection_use'] == json_object['data']['ethereum_connection_use']
        assert serialized_object['data']['ipfs_connection_host'] == json_object['data']['ipfs_connection_host']
        assert serialized_object['data']['ipfs_connection_use'] == json_object['data']['ipfs_connection_use']
        assert serialized_object['data']['pandora_contract_address'] == json_object['data']['pandora_contract_address']
        assert serialized_object['data']['pynode_config_file_path'] == json_object['data']['pynode_config_file_path']
        assert serialized_object['data']['pynode_launch_mode'] == json_object['data']['pynode_launch_mode']
        assert serialized_object['data']['worker_contract_address'] == json_object['data']['worker_contract_address']

        assert serialized_object['object_type'] == json_object['object_type']

    def test_model_for_status(self):
        status = PynodeStatus()
        status.define_object(state='Online',
                             ethereum_host='http://rinkeby.pandora.network:8545',
                             ipfs_host='http://ipfs.pandora.network',
                             pandora_address='0x9f301cfd1217fd60e4244a12b1edffe458e8b9bd',
                             worker_address='0x6ac66706c9eF0b2A6eD6B471fb2d086d0C7BC055',
                             worker_state='IDLE',
                             job_address='',
                             job_status='',
                             kernel_address='',
                             dataset_address='',
                             job_result_address='')
        serialized_status = str.encode(ClassApiSerializer().serialize(status))
        serialized_object = json.loads(serialized_status)
        json_object =  json.loads("""
        {"data": {
            "dataset_address": "", 
            "ethereum_host": "http://rinkeby.pandora.network:8545", 
            "ipfs_host": "http://ipfs.pandora.network", 
            "job_address": "", 
            "job_result_address": "", 
            "job_status": "", 
            "kernel_address": "", 
            "pandora_address": "0x9f301cfd1217fd60e4244a12b1edffe458e8b9bd", 
            "state": "Online", 
            "worker_address": "0x6ac66706c9eF0b2A6eD6B471fb2d086d0C7BC055", 
            "worker_status": "IDLE"
            }, 
            "object_type": "PynodeStatus"
        }""")

        assert serialized_object['data']['state'] == json_object['data']['state']
        assert serialized_object['data']['ethereum_host'] == json_object['data']['ethereum_host']
        assert serialized_object['data']['ipfs_host'] == json_object['data']['ipfs_host']
        assert serialized_object['data']['pandora_address'] == json_object['data']['pandora_address']
        assert serialized_object['data']['worker_address'] == json_object['data']['worker_address']
        assert serialized_object['data']['worker_status'] == json_object['data']['worker_status']
        assert serialized_object['data']['job_address'] == json_object['data']['job_address']
        assert serialized_object['data']['job_status'] == json_object['data']['job_status']
        assert serialized_object['data']['kernel_address'] == json_object['data']['kernel_address']
        assert serialized_object['data']['dataset_address'] == json_object['data']['dataset_address']
        assert serialized_object['data']['job_result_address'] == json_object['data']['job_result_address']

        assert serialized_object['object_type'] == json_object['object_type']


