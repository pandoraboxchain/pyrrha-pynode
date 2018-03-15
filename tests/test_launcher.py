import logging
import threading
import sys
import os
import json
import unittest

from manager import Manager
from broker import Broker
from tests.core.base_test_core import BaseCoreConfiguration
from tests.core.base_test_listener import BaseTestListener
from configparser import ConfigParser

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )


class TestManager:

    host = None
    test_listener = None
    test_listener_thread = None
    test_core_configuration = None

    # get customer configured primary contracts addresses
    pandora_contract_address = None
    worker_contract_address = None

    # on init read configuration for running tests
    def __init__(self, *host):
        manager = Manager.get_instance()
        if manager.test_host is None:
            if host:
                # if config file set manually
                instantiate_manager(host[0])
            else:
                # if launch only listener from test_manager as launcher
                instantiate_manager('../pynode.ini')
        self.host = manager.eth_host
        self.pandora_contract_address = manager.eth_pandora
        self.worker_contract_address = manager.eth_worker

    def get_test_listener_host(self) -> str:
        return self.host

    def get_configuration(self) -> BaseCoreConfiguration:
        self.test_core_configuration = BaseCoreConfiguration.get_instance()
        return self.test_core_configuration

    def run_test_listener(self, demon: bool = False):
        # run test listener in new daemon thread
        print("Launch mok eth listener on host : " + self.host)
        self.test_listener = BaseTestListener(host=self.host, configuration=self.test_core_configuration)
        self.test_listener_thread = threading.Thread(target=self.test_listener.launch)
        if demon:
            self.test_listener_thread.daemon = True
        self.test_listener_thread.start()
        print('Listener started in demon mode  : ' + str(demon))

    def stop_test_listener(self):
        self.test_listener.stop()
        self.test_listener_thread.join()

    @staticmethod
    def run_test_pynode(*config_file) -> int:
        try:
            manager = Manager.get_instance()
            print("Launch pynode for tests on host  : " + str(manager.eth_host))
            broker = Broker(eth_server=manager.eth_host,
                            abi_path="../" + manager.eth_abi_path,
                            pandora=manager.eth_pandora,
                            node=manager.eth_worker,
                            data_dir="../" + manager.ipfs_storage,
                            ipfs_server=manager.ipfs_host,
                            ipfs_port=manager.ipfs_port)
        except Exception as ex:
            logging.error("Error launching pynode for tests")
            logging.error(ex.args)
            raise

        try:
            broker.connect()
        except Exception as ex:
            logging.error("Error connecting pynode for tests host")
            logging.error(ex.args)
            raise

        broker.join()
        return 1


def instantiate_manager(config_file_path: str):
    manager = Manager.get_instance()
    # setup default test host
    test_host = 'http://localhost:4000'
    # read configs
    print("Configuration file path      : " + str(config_file_path))
    if config_file_path:
        try:
            config = ConfigParser()
            config.read(config_file_path)
            eth_contracts = config['Contracts']
            ipfs_section = config['IPFS']
            pandora_address = eth_contracts['pandora']
            worker_address = eth_contracts['worker_node']
            ipfs_storage = ipfs_section['store_in']
            ipfs_use_section = config['IPFS.%s' % 'local']
            ipfs_host = ipfs_use_section['server']
            ipfs_port = ipfs_use_section['port']
        except Exception as ex:
            print("Error reading config: %s, exiting", type(ex))
            logging.error(ex.args)
            return
    print("Config reading success")

    manager.launch_mode = 1
    manager.eth_host = test_host
    manager.eth_abi_path = config_file_path
    manager.eth_pandora = pandora_address
    manager.eth_worker = worker_address
    manager.ipfs_storage = ipfs_storage
    manager.ipfs_host = ipfs_host
    manager.ipfs_port = ipfs_port
    manager.test_host = test_host
    # instantiate contracts
    abi_path = config_file_path.replace("pynode.ini", "abi")
    instantiate_contracts(abi_path, True)


def instantiate_contracts(abi_path, eth_hooks):
    manager = Manager.get_instance()
    if os.path.isdir(abi_path):
        print("ABI folder path              : " + str(abi_path))
        if eth_hooks:
            if os.path.isfile(abi_path + "\PandoraHooks.json"):
                with open(abi_path + "\PandoraHooks.json", encoding='utf-8') as pandora_contract_file:
                    manager.eth_pandora_contract = json.load(pandora_contract_file)['abi']
        else:
            if os.path.isfile(abi_path + "\Pandora.json"):
                with open(abi_path + "\Pandora.json", encoding='utf-8') as pandora_contract_file:
                    manager.eth_pandora_contract = json.load(pandora_contract_file)['abi']

        if os.path.isfile(abi_path + "\WorkerNode.json"):
            with open(abi_path + "\WorkerNode.json", encoding='utf-8') as worker_contract_file:
                manager.eth_worker_contract = json.load(worker_contract_file)['abi']
        if os.path.isfile(abi_path + "\CognitiveJob.json"):
            with open(abi_path + "\CognitiveJob.json", encoding='utf-8') as eth_cognitive_job_contract:
                manager.eth_cognitive_job_contract = json.load(eth_cognitive_job_contract)['abi']
        if os.path.isfile(abi_path + "\Kernel.json"):
            with open(abi_path + "\Kernel.json", encoding='utf-8') as eth_kernel_contract:
                manager.eth_kernel_contract = json.load(eth_kernel_contract)['abi']
        if os.path.isfile(abi_path + "\CognitiveJob.json"):
            with open(abi_path + "\Dataset.json", encoding='utf-8') as eth_dataset_contract:
                manager.eth_dataset_contract = json.load(eth_dataset_contract)['abi']
        print("ABI loading success")
    else:
        print("ABI files not found, exiting")
        return


def launch_moc_service(*args):
    TestManager('../pynode.ini')
    loader = unittest.TestLoader()
    # acceptance test launcher
    start_dir = 'acceptance'
    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite)


if __name__ == "__main__":
    launch_moc_service(sys.argv)
