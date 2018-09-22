import os
import sys
import argparse
import logging
import json

from configparser import ConfigParser

from core.manager import Manager
from core.broker import Broker
from core.patterns.exceptions import ContractsAbiNotFound

from service.webapi.web_socket_listener import WebSocket


# -------------------------------------
# main pynode launcher
# -------------------------------------
def run_pynode():
    try:
        manager = Manager.get_instance()
        # startup broker main process
        broker = Broker(eth_server=manager.eth_host,
                        abi_path=manager.eth_abi_path,
                        pandora=manager.eth_pandora,
                        node=manager.eth_worker,
                        data_dir=manager.ipfs_storage,
                        ipfs_server=manager.ipfs_host,
                        ipfs_port=manager.ipfs_port)
    except Exception as ex:
        logging.error("Error broker initialization: %s, exiting", type(ex))
        logging.error(ex.args)
        return

    if broker.connect() is True:
        return

    # Remove the following line in order to put the app into a daemon mode (running on the background)
    if broker.is_alive():
        broker.join()


# -------------------------------------
# primary pynode enter point
# -------------------------------------
def main(argv):
    help_message = """
        Pandora Boxchain python node realisation    
        
                -/////////+++++/`                
             `/ss:--:sds/d/````.hNso-             
           /hNhsoosh+.   `h+     ss`/ss`          
          so     yoh/      yy//+++dh- /h`         
         y+    `h/  yo  -ohM+...`.d+/sssm-        
       `hh++++od/    sds/-h:    `h:    -sN/       
      `dN`````-Mh`  .d- -mo::::/m:     `h/yo      
     .d:m     `m:d.-d/os++yds:-.:os+. .d-  oy`    
    -d.`m     `m .dmy/`     -ossooshNdN-    +d    
    so :Mhoooood: so          :Mh`    :d.  -NM    
    so/h`y+     y++o          :d:d.    .d-:d.N    
    sNs   os     oNo          -d .dsoooosNd``N`   
    :d     dhmdsooyyo:      -odm: s+     os +y    
     :h` `y/ `/oo/..-+hh+:os+ho`y+o+     osos     
      .h:h:     `d+/////N/ `y+   oNo     +Mo      
       `dh:    .h-    `h:-oyh    `dsoo++oN+       
        `yyos+:d-````-mds/` /h` `h:    `h/        
          oo .oN+++++od`     -h:d-    `h:         
           /s/`/h`    :h.    -shyoosmmh-          
             .+shd.    .d:/ss/` `/ss/`            
                `/ooo+++oooo+++++-                
                                                     
        to see more https://pandoraboxchain.ai/ 
        
        Current configuration performs launch with different parameters and configurations
         
        example >python ./pynode.py -p <your vault password>
                                    - starts pynode with default config 
                                      placed in pynode.ini file 
        ATTENTION! - vault password is necessary, and if you use docker and if you use the docker, 
        enter the password in the startup line in Dockerfile

        if we need launch with different ETH HOST and IPFS config use launch params
        example >python ./pynode.py -e (--ethereum) remote -i (--ipfs) pandora
                    with eth_connector instance to connect remote  = http://rinkeby.pandora.network:8545
                    and IPFS config server = http://ipfs.pandora.network
                                             port = 5001

        -c (--config) performs path for custom config file for launch params
        -a (--abi) performs change abi directory path

        -w (--worker) alow to set custom worker contract address
                      seted by console value will replace value in config file
                      for this launch                     
    """

    parser = argparse.ArgumentParser(description=help_message, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-p',
                        '--password',
                        action="store",
                        dest='vault_key',
                        default='',
                        help='necessary parameter for launch pynode.'
                             '(used for encrypt vault and use private key to local transactions sign)',
                        metavar='')
    parser.add_argument('-c',
                        '--config',
                        action="store",
                        dest='configuration_file',
                        default='../pynode/core/config/pynode.ini',
                        help='startup pyrrha-pynode with custom configuration file '
                             '(default is ../pynode.ini strongly recommended for use)',
                        metavar='')
    parser.add_argument('-e',
                        '--ethereum',
                        action="store",
                        dest='ethereum_use',
                        default='remote',
                        help='setting up current used host for ethereum node '
                             '(default is remote)',
                        metavar='')
    parser.add_argument('-a',
                        '--abi',
                        action='store',
                        dest='abi_path',
                        default='../pyrrha-consensus/build/contracts/',
                        help='setting up path to folder with ABI files '
                             '(default is ../abi/ strongly recommended for use)',
                        metavar='')
    parser.add_argument('-i',
                        '--ipfs',
                        action='store',
                        dest='ipfs_use',
                        default='pandora',
                        help='setting up current used host for ipfs connection '
                             '(default is "pandora" strongly recommended for use)',
                        metavar='')
    parser.add_argument('-v ',
                        '--version',
                        action='version',
                        version='%(prog)s 0.1.2')

    results = parser.parse_args()

    # read configuration file and parse base settings
    print("Configuration file path      : " + str(results.configuration_file))
    if results.configuration_file:
        try:
            config = ConfigParser()
            config.read(results.configuration_file)
            eth_section = config['Ethereum']
            account_section = config['Account']
            eth_contracts = config['Contracts']
            ipfs_section = config['IPFS']
            web_section = config['Web']
            eth_host = eth_section[results.ethereum_use]
            eth_worker_node_account = account_section['worker_node_account']
            pandora_address = eth_contracts['pandora']
            worker_address = eth_contracts['worker_node']
            eth_hooks = eth_contracts['hooks']
            pynode_start_on_launch = eth_contracts['start_on_launch']
            ipfs_storage = ipfs_section['store_in']
            ipfs_use_section = config['IPFS.%s' % results.ipfs_use]
            ipfs_host = ipfs_use_section['server']
            ipfs_port = ipfs_use_section['port']
            socket_enable = web_section['enable']
            socket_host = web_section['host']
            socket_port = web_section['port']
            socket_listen = web_section['connections']
        except Exception as ex:
            print("Error reading config: %s, exiting", type(ex))
            logging.error(ex.args)
            return
    print("Config reading success")
    manager = Manager.get_instance()
    if not results.vault_key:
        print('Vault key is necessary for launch (use -p key for provide if)')
        return
    manager.primary_wd = os.getcwd()
    manager.vault_key = results.vault_key
    # -------------------------------------
    # launch pynode
    # -------------------------------------
    worker_contract_address = worker_address

    manager.pynode_config_file_path = results.configuration_file
    manager.launch_mode = "0"  # results.launch_mode
    manager.eth_use = results.ethereum_use
    manager.eth_host = eth_host

    manager.eth_worker_node_account = eth_worker_node_account

    manager.eth_abi_path = results.abi_path
    manager.eth_pandora = pandora_address
    manager.eth_worker = worker_contract_address
    manager.ipfs_use = results.ipfs_use
    manager.ipfs_host = ipfs_host
    manager.ipfs_port = ipfs_port
    manager.ipfs_storage = ipfs_storage
    manager.pynode_start_on_launch = pynode_start_on_launch
    manager.web_socket_enable = socket_enable
    manager.web_socket_host = socket_host
    manager.web_socket_port = socket_port
    manager.web_socket_listeners = socket_listen

    print("Pynode production launch")
    print("Node launch mode             : " + str(manager.launch_mode))
    print("Ethereum use                 : " + str(results.ethereum_use))
    print("Ethereum host                : " + str(eth_host))
    print("Worker node account owner    : " + str(eth_worker_node_account))
    print("Use vault password           : " + str(manager.vault_key))
    print("Primary contracts addresses")
    print("Pandora main contract        : " + str(pandora_address))
    print("Worker node contract         : " + str(worker_contract_address))
    print("IPFS configuration")
    print("IPFS use                     : " + str(results.ipfs_use))
    print("IPFS host                    : " + str(ipfs_host))
    print("IPFS port                    : " + str(ipfs_port))
    print("IPFS file storage            : " + str(ipfs_storage))
    print("Web socket enable            : " + str(socket_enable))
    # inst contracts
    instantiate_contracts(results.abi_path, eth_hooks)
    # launch socket web listener
    if socket_enable == 'True':
        print("Launch client socket listener")
        print("Web socket enable            : " + str(manager.web_socket_enable))
        print("Web socket host              : " + str(manager.web_socket_host))
        print("Web socket port              : " + str(manager.web_socket_port))
        print("Web socket listeners         : " + str(manager.web_socket_listeners))
        WebSocket(socket_host, socket_port, socket_listen)
    # launch pynode
    if pynode_start_on_launch == 'True':
        print("Launch pynode...")
        run_pynode()


# -------------------------------------
# read and store contracts abi
# -------------------------------------
def instantiate_contracts(abi_path, eth_hooks):
    manager = Manager.get_instance()
    print("ABI folder path              : " + str(abi_path))
    if os.path.isdir(abi_path):
        if eth_hooks == 'True':
            if os.path.isfile(abi_path + "PandoraHooks.json"):
                with open(abi_path + "PandoraHooks.json", encoding='utf-8') \
                        as pandora_contract_file:
                    manager.eth_pandora_contract = json.load(pandora_contract_file)['abi']
                    print('Pandora hooks abi loaded')
        else:
            if os.path.isfile(abi_path + "Pandora.json"):
                with open(abi_path + "Pandora.json", encoding='utf-8') \
                        as pandora_contract_file:
                    manager.eth_pandora_contract = json.load(pandora_contract_file)['abi']
                    print('Pandora abi loaded')

        if os.path.isfile(abi_path + "WorkerNode.json"):
            with open(abi_path + "WorkerNode.json", encoding='utf-8') \
                    as worker_contract_file:
                manager.eth_worker_contract = json.load(worker_contract_file)['abi']
                print('WorkerNode abi loaded')
        if os.path.isfile(abi_path + "CognitiveJobController.json"):
            with open(abi_path + "CognitiveJobController.json", encoding='utf-8') \
                    as eth_job_controller_contract:
                manager.eth_job_controller_contract = json.load(eth_job_controller_contract)['abi']
                print('CognitiveJobController abi loaded')
        if os.path.isfile(abi_path + "Kernel.json"):
            with open(abi_path + "Kernel.json", encoding='utf-8') \
                    as eth_kernel_contract:
                manager.eth_kernel_contract = json.load(eth_kernel_contract)['abi']
                print('Kernel abi loaded')
        if os.path.isfile(abi_path + "Dataset.json"):
            with open(abi_path + "Dataset.json", encoding='utf-8') \
                    as eth_dataset_contract:
                manager.eth_dataset_contract = json.load(eth_dataset_contract)['abi']
                print('Dataset abi loaded')

    else:
        print("ABI files not found, exiting.")
        print("pyrrha-pynode repo contains link to pyrrha-consensus project.")
        print("for complete clone project please provide git commands :")
        print("cd .\pyrrha-pynode\"")
        print("git submodule init")
        print("git submodule update --recursive --remote")
        raise ContractsAbiNotFound()


# -------------------------------------
# main launcher
# -------------------------------------
if __name__ == "__main__":
    # set base project folder
    if 'tests' in os.getcwd():
        os.chdir('../')
    main(sys.argv)

