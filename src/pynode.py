import sys
import os
import unittest
import logging
import argparse
import json

from configparser import ConfigParser
from broker import Broker
from manager import Manager

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )


def run_pynode():
    try:
        manager = Manager.get_instance()
        broker = Broker(eth_server=manager.eth_host,
                        abi_path=manager.eth_abi_path,
                        pandora=manager.eth_pandora,
                        node=manager.eth_worker,
                        data_dir=manager.ipfs_storage,
                        ipfs_server=manager.ipfs_host,
                        ipfs_port=manager.ipfs_port)
    except Exception as ex:
        logging.error("Error reading config: %s, exiting", type(ex))
        logging.error(ex.args)
        return

    if broker.connect() is False:
        return

    # Remove the following line in order to put the app into a daemon mode (running on the background)
    broker.join()


def run_tests():
    loader = unittest.TestLoader()
    start_dir = 'test/acceptance'
    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite)


def main(argv):
    """Parses command-line options and evokes `run`"""
    parser = argparse.ArgumentParser()

    parser.add_argument('-m',
                        '--mode',
                        action="store",
                        dest='launch_mode',
                        default='0',
                        help='launch mode for pynode, '
                             'set value "1" for launch in strict, develop mode (default value is 0)')
    parser.add_argument('-c',
                        '--config',
                        action="store",
                        dest='configuration_file',
                        default='../pynode.ini',
                        help='startup pyrrha-pynode with custom configuration file (default is ../pynode.ini)')
    parser.add_argument('-e',
                        '--ethereum',
                        action="store",
                        dest='ethereum_use',
                        default='ganache',
                        help='setting up current used host for ethereum node (default is local)')
    parser.add_argument('-a',
                        '--abi',
                        action='store',
                        dest='abi_path',
                        default='../abi',
                        help='setting up path to folder with ABI files (default is ../../abi)')
    parser.add_argument('-i',
                        '--ipfs',
                        action='store',
                        dest='ipfs_use',
                        default='local',
                        help='setting up current used host for ipfs connection (default is local)')
    parser.add_argument('-w',
                        '--worker',
                        action='store',
                        dest="worker_node",
                        help='setting up currently created worker contract address ')
    parser.add_argument('-d',
                        '--dockerize',
                        action='store',
                        dest='prep_docker_config',
                        default=False,
                        help='prepare node configuration for using in as doker image')
    parser.add_argument('-t',
                        '--test',
                        action="store",
                        dest='run_test',
                        default=False,
                        help='setup host for launch tests')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s 0.9.1')

    results = parser.parse_args()

    # read configuration file and parse base settings
    print("Configuration file path      : " + str(results.configuration_file))
    if results.configuration_file:
        try:
            config = ConfigParser()
            config.read(results.configuration_file)
            eth_section = config['Ethereum']
            eth_contracts = config['Contracts']
            ipfs_section = config['IPFS']
            eth_host = eth_section[results.ethereum_use]
            pandora_address = eth_contracts['pandora']
            worker_address = eth_contracts['worker_node']
            eth_hooks = eth_contracts['hooks']
            ipfs_storage = ipfs_section['store_in']
            ipfs_use_section = config['IPFS.%s' % results.ipfs_use]
            ipfs_host = ipfs_use_section['server']
            ipfs_port = ipfs_use_section['port']
        except Exception as ex:
            print("Error reading config: %s, exiting", type(ex))
            logging.error(ex.args)
            return
    print("Config reading success")

    manager = Manager.get_instance()
    if results.run_test:
        # setup default test host
        test_host = 'http://localhost:4000'
        manager.launch_mode = 1
        manager.eth_host = test_host
        manager.eth_abi_path = results.abi_path
        manager.eth_pandora = pandora_address
        manager.eth_worker = worker_address
        manager.ipfs_storage = ipfs_storage
        manager.ipfs_host = ipfs_host
        manager.ipfs_port = ipfs_port
        manager.test_host = test_host

        print("Pynode test launch")
        print("Node launch mode             : " + str(1))
        print("Ethereum host                : " + str(test_host))
        print("Test listener                : " + str(test_host))
        print("Base pynode configuration")
        print("Pandora main contract        : " + str(pandora_address))
        print("Worker node contract         : " + str(worker_address))
        print("IPFS host                    : " + str(ipfs_host))
        print("IPFS port                    : " + str(ipfs_port))
        print("IPFS file storage            : " + str(ipfs_storage))
        # inst contracts
        instantiate_contracts(results, eth_hooks)
        # launch tests
        run_tests()
        print("Launch tests")
    elif results.prep_docker_config:
        print("Prepare configs for docker container creation")
        # uncomment for
        # use_env_cfg()
    else:
        print("Node launch mode             : " + str(results.launch_mode))
        print("Ethereum use                 : " + str(results.ethereum_use))
        print("Ethereum host                : " + str(eth_host))
        print("Primary contracts addresses")
        print("Pandora main contract        : " + str(pandora_address))
        if results.worker_node:
            worker_contract_address = results.worker_node
        else:
            worker_contract_address = worker_address
        print("Worker node contract         : " + str(worker_contract_address))
        print("IPFS configuration")
        print("IPFS use                     : " + str(results.ipfs_use))
        print("IPFS host                    : " + str(ipfs_host))
        print("IPFS port                    : " + str(ipfs_port))
        print("IPFS file storage            : " + str(ipfs_storage))

        manager.launch_mode = results.launch_mode
        manager.eth_host = eth_host
        manager.eth_abi_path = results.abi_path
        manager.eth_pandora = pandora_address
        manager.eth_worker = worker_contract_address
        manager.ipfs_host = ipfs_host
        manager.ipfs_port = ipfs_port
        manager.ipfs_storage = ipfs_storage
        # inst contracts
        instantiate_contracts(results, eth_hooks)
        # launch pynode
        print("Launch node")
        run_pynode()


def instantiate_contracts(results, eth_hooks):
    manager = Manager.get_instance()
    if os.path.isdir(results.abi_path):
        print("ABI folder path              : " + str(results.abi_path))
        if eth_hooks:
            if os.path.isfile(results.abi_path + "\PandoraHooks.json"):
                with open(results.abi_path + "\PandoraHooks.json", encoding='utf-8') as pandora_contract_file:
                    manager.eth_pandora_contract = json.load(pandora_contract_file)['abi']
        else:
            if os.path.isfile(results.abi_path + "\Pandora.json"):
                with open(results.abi_path + "\Pandora.json", encoding='utf-8') as pandora_contract_file:
                    manager.eth_pandora_contract = json.load(pandora_contract_file)['abi']

        if os.path.isfile(results.abi_path + "\WorkerNode.json"):
            with open(results.abi_path + "\WorkerNode.json", encoding='utf-8') as worker_contract_file:
                manager.eth_worker_contract = json.load(worker_contract_file)['abi']
        if os.path.isfile(results.abi_path + "\CognitiveJob.json"):
            with open(results.abi_path + "\CognitiveJob.json", encoding='utf-8') as eth_cognitive_job_contract:
                manager.eth_cognitive_job_contract = json.load(eth_cognitive_job_contract)['abi']
        if os.path.isfile(results.abi_path + "\Kernel.json"):
            with open(results.abi_path + "\Kernel.json", encoding='utf-8') as eth_kernel_contract:
                manager.eth_kernel_contract = json.load(eth_kernel_contract)['abi']
        if os.path.isfile(results.abi_path + "\CognitiveJob.json"):
            with open(results.abi_path + "\Dataset.json", encoding='utf-8') as eth_dataset_contract:
                manager.eth_dataset_contract = json.load(eth_dataset_contract)['abi']
        print("ABI loading success")
    else:
        print("ABI files not found, exiting")
        return


if __name__ == "__main__":
    main(sys.argv)


def use_env_cfg():
    config_tmp = open('../pynode.tmp.ini', "r")
    config_file = open('../pynode.ini', "w")
    while 1:
        line = config_tmp.readline()
        if not line: break
        if os.environ['ETHEREUM_HOST']: line = line.replace('ETHEREUM_HOST', os.environ['ETHEREUM_HOST'])
        if os.environ['ETHEREUM_LOCAL_HOST']: line = line.replace('ETHEREUM_LOCAL_HOST', os.environ['ETHEREUM_LOCAL_HOST'])
        if os.environ['IPFS_INFURA_HOST']: line = line.replace('IPFS_INFURA_HOST', os.environ['IPFS_INFURA_HOST'])
        if os.environ['IPFS_PANDORA_HOST']: line = line.replace('IPFS_PANDORA_HOST', os.environ['IPFS_PANDORA_HOST'])
        if os.environ['IPFS_LOCALHOST']: line = line.replace('IPFS_LOCALHOST', os.environ['IPFS_LOCALHOST'])
        if os.environ['CONTRACT_PANDORA']: line = line.replace('CONTRACT_PANDORA', os.environ['CONTRACT_PANDORA'])
        if os.environ['CONTRACT_WORKER_NODE']: line = line.replace('CONTRACT_WORKER_NODE', os.environ['CONTRACT_WORKER_NODE'])
        config_file.write(line)
    config_file.close()
    config_tmp.close()
    print('=======================================')
    print(open('../pynode.ini').read())
    print('=======================================')

