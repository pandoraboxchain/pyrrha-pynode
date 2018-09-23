import sys
import os
import argparse
import json
import time
import base64
from base64 import b64encode

from configparser import ConfigParser
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

from pathlib import Path
from hashlib import md5
from Crypto import Random
from Crypto.Cipher import AES
from threading import Thread


# -------------------------------------------------
# Main model for data storing
# -------------------------------------------------
class MainModel:
    eth_host = None
    pandora_contract_address = None
    pandora_abi_path = None
    pandora_abi = None
    remove_flag = False
    current_worker_contract = None

    new_worker_account = None
    new_worker_account_vault_pass = None
    new_worker_account_p_key = None
    obtaining_flag = False
# -------------------------------------------------


# -------------------------------------------------
# main process for worker contract creation
# -------------------------------------------------
def process_create_worker_contract():
    # init connection and pandora contract
    connector = Web3(HTTPProvider(MainModel.eth_host))
    # insert PoA(for example rinkeby) integration and check version
    connector.middleware_stack.inject(geth_poa_middleware, layer=0)
    try:
        synk_info = connector.eth.syncing
    except Exception as ex:
        print('Unable to connect to eth node')
        raise Exception('Unable to connect to eth node')
    if synk_info is not False:
        print('Eth node in synking mode, try later')
        raise Exception('Eth node in synking mode, try later')

    print('Connection success, check provided customer account address')
    contract = connector.eth.contract(address=connector.toChecksumAddress(MainModel.pandora_contract_address),
                                      abi=MainModel.pandora_abi)

    worker = Thread()  # assign empty for join
    if MainModel.remove_flag is False:
        # -------------------------
        # On Create() logic start
        # -------------------------
        # for provide possibility use current created worker node contract with vault
        # provide vault recreation before account balance validate
        MainModel.new_worker_account_p_key = obtain_private_key()
        MainModel.new_worker_account_vault_pass = obtain_local_password()
        vault_result = create_vault(MainModel.new_worker_account_vault_pass,
                                    MainModel.new_worker_account,
                                    MainModel.new_worker_account_p_key)
        if not vault_result:
            print('Unable to create vault.')
            return

        account_balance = connector.eth.getBalance(connector.toChecksumAddress(
            connector.toChecksumAddress(MainModel.new_worker_account)))
        account_balance_eth = Web3.fromWei(account_balance, 'ether')
        if account_balance_eth < 0.5:
            print('For creating worker node account your need to spend 0.005 ETH and 0.5 ETH need for management node')
            print('If your currently create worker node contract, you can try start pynode with current configuration')
            print('Unable to create worker contract. Exit.')
            return

        # for performing test ask not from latest block
        filter_on_worker = contract.events.WorkerNodeCreated.createFilter(fromBlock='latest')
        worker = Thread(target=filter_thread_loop, args=(filter_on_worker, 2), daemon=False)
        worker.start()
        status = worker.is_alive()
        print('Event listener for worker node creation startup success, alive : ' + str(status))
        # -------------------------
        # On Create() logic finish
        # -------------------------
    else:
        # -------------------------
        # On Delete() logic start
        # -------------------------
        print('Deletion is FORCE operation, be sure of their actions.')
        MainModel.new_worker_account_p_key = obtain_private_key()
        print('Connection success, check provided customer account address')
        contract = connector.eth.contract(address=connector.toChecksumAddress(MainModel.pandora_contract_address),
                                          abi=MainModel.pandora_abi)

        # for performing test ask not from latest block
        filter_on_worker = contract.events.WorkerNodeDestroyed.createFilter(fromBlock='latest')
        worker = Thread(target=filter_thread_loop, args=(filter_on_worker, 2), daemon=False)
        worker.start()
        status = worker.is_alive()
        print('Event listener for worker node destroy startup success, alive : ' + str(status))
        # -------------------------
        # On Delete() logic finish
        # -------------------------

    print('Provide gas estimation')
    connector.eth.setGasPriceStrategy(medium_gas_price_strategy)
    gas_estimation = connector.eth.generateGasPrice()
    gas_estimation = int(gas_estimation * 4)
    gas_price = connector.eth.gasPrice
    print('Gas estimation complete success')
    checksum_worker_node_account = connector.toChecksumAddress(MainModel.new_worker_account)
    if MainModel.remove_flag is False:
        print('Transact for creation worker node contract')
        try:
            nonce = connector.eth.getTransactionCount(checksum_worker_node_account, "pending")
            raw_transaction = contract.functions.createWorkerNode() \
                .buildTransaction({
                    'from': checksum_worker_node_account,
                    'nonce': nonce,
                    'gas': gas_estimation,
                    'gasPrice': int(gas_price)})
            signed_transaction = connector.eth.account.signTransaction(raw_transaction,
                                                                       MainModel.new_worker_account_p_key)
            MainModel.new_worker_account_p_key = None
            tx_hash = connector.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print('TX_HASH : ' + tx_hash.hex())
            print('Waiting for receipt...')
            transaction_receipt = connector.eth.waitForTransactionReceipt(tx_hash, timeout=300)  # may take while(5 min)
            print('TX_RECEIPT : ' + str(transaction_receipt))
            print('TRANSACTION_STATUS = ' + str(transaction_receipt['status']))
        except Exception as ex:
            print('Exception while transact creation worker contract')
            print(ex.args)
            return
    else:
        print('Transact for destroy worker node contract')
        try:
            nonce = connector.eth.getTransactionCount(checksum_worker_node_account)
            raw_transaction = contract.functions.destroyWorkerNode(MainModel.current_worker_contract) \
                .buildTransaction({
                    'from': checksum_worker_node_account,
                    'nonce': nonce,
                    'gas': gas_estimation,
                    'gasPrice': int(gas_price)})
            signed_transaction = connector.eth.account.signTransaction(raw_transaction,
                                                                       MainModel.new_worker_account_p_key)
            MainModel.new_worker_account_p_key = None
            tx_hash = connector.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print('TX_HASH : ' + tx_hash.hex())
            print('Waiting for receipt...')
            transaction_receipt = connector.eth.waitForTransactionReceipt(tx_hash, timeout=300)  # may take while(5 min)
            print('TX_RECEIPT : ' + str(transaction_receipt))
            print('TRANSACTION_STATUS = ' + str(transaction_receipt['status']))
        except Exception as ex:
            print('Exception while transact destroy worker contract')
            print(ex.args)
            return
    if transaction_receipt['status'] == 0:
        print('Transaction fail. For technical support please save logs and contact with us.')
        exit(0)
    return


def filter_thread_loop(event_filter, poll_interval):
    while True:
        try:
            for event in event_filter.get_all_entries():
                on_worker_node_event(event)
            time.sleep(poll_interval)
        except Exception as ex:
            print('Exception on event handler.')
            print(ex.args)


def on_worker_node_event(event: dict):
    if MainModel.remove_flag is False:
        try:
            address = event['args']['workerNode']
            print("Node creation success address : " + address)
            print("Storing worker address to config file")
            config = ConfigParser()
            config.read('../pynode/core/config/pynode.ini')

            cfg_file = open('../pynode/core/config/pynode.ini', 'w')
            config.set('Contracts', 'worker_node', str(address))
            config.set('Account', 'worker_node_account', str(MainModel.new_worker_account))
            config.write(cfg_file)
            cfg_file.close()
        except Exception as ex:
            print("Exception retrieving worker contract address")
            print(ex.args)
        print("Address is stored in default config file on Ethereum section")
        print("Please save the address in order to avoid losing it")
        print("Pynode is configured and ready for launch with default parameters and your vault password")
        MainModel.obtaining_flag = True
    else:
        try:
            print(event['args'])
            MainModel.obtaining_flag = True
        except Exception as ex:
            print("Exception retrieving worker contract deletion event")
            print(ex.args)
    exit(0)
# -------------------------------------------------


# -------------------------------------------------
# Internal methods
# -------------------------------------------------
def obtain_local_password():
    customer_vault_password = input('Provide vault password (min 7 characters) : ')
    if len(customer_vault_password) < 6:
        print('Password to short, please try again (min 7 characters)')
        obtain_local_password()
    return customer_vault_password


def obtain_private_key() -> str:
    customer_account_private_key = input('Provide worker account owner private key : ')
    try:
        base64.decodebytes(customer_account_private_key.encode())
    except Exception:
        print('Incorrect account private key, please try again')
        obtain_private_key()
    if base64.decodebytes(customer_account_private_key.encode()) is not '':
        return customer_account_private_key
    else:
        print('Incorrect account private key, please try again')
        obtain_private_key()


def create_vault(local_password: str, new_worker_account: str, worker_account_private: str) -> bool:
    # recreate password vault
    vault_folder = Path('../pynode/vault')
    if os.path.exists(vault_folder) is False:
        os.makedirs(vault_folder)
    vault_file = Path(str(vault_folder) + '/worker_node_key.pri')
    if os.path.isfile(vault_file) is False:
        open(vault_file, 'a').close()
    # prepare for encoding
    block_size = 16
    pad = lambda s: s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)
    # encode and store local password
    try:
        vault_password = md5(local_password.encode('utf8')).hexdigest()
        raw = pad(new_worker_account + "_" + worker_account_private).encode('utf8')
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(vault_password.encode('utf8'), AES.MODE_CBC, iv)
        result = b64encode(iv + cipher.encrypt(raw))
        vault_file = open(vault_file, "wb")
        vault_file.write(result)
        vault_file.close()
    except Exception as ex:
        print('Exception due vault creation. Exiting')
        print(ex.args)
        return False
    print('Secure vault creation success')
    return True
# -------------------------------------------------


# -------------------------------------------------
# Main launch method for params getting and self configuration
# -------------------------------------------------
def main(argv):
    help_message = """
            Pandora Boxchain python tool for worker contract management

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

            Current tool allows to create worker node contract for working in Pandora environment.
            Worker node account is belongs to your worker node and provide possibility to get and calculate
            provided jobs offering. All complete jobs rewords will be sended to your worker account.
            Please do not use your primary account.
            
            For prepare you worker node account for work you will need to provide account private key for account import
            and provide unlocking account for transact node states
            
            Usage:
                -a (--account) - use this flag for provide worker node account address
                                 (account must be whitelisted for providing this operation,
                                 and must contain about 4ETH on its balance)
                -r (--remove) - use this flag to destroy worker node contract for your account
            example >python ./worker_tools.py -a <owner_account_address> -r
                                  
            Current tool try to import your account and ask for local password and account private key,
            private key will be stored in secured vault and will be used for signing state transactions locally. 
            This password is only actual for pandora ethereum node current instance, do not forget it).
            
            WARNING: Current operation will overwrites your key vault and default config pynode.ini 
            (worker contract address automatically filled in) please back up your vault and pynode 
            configuration file to prevent data loss
            """

    parser = argparse.ArgumentParser(description=help_message, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-a',
                        '--account',
                        action="store",
                        dest='new_worker_account',
                        default='0',
                        help='provide an account, '
                             'this account will be whitelisted',
                        metavar='')
    parser.add_argument('-r',
                        '--remove',
                        action='store_true',
                        dest="remove_account",
                        default='False',
                        help='flag for remove account from whitelist')

    results = parser.parse_args()
    print('Try read config, instantiate abi and provide operation')
    try:
        config = ConfigParser()
        config.read('../pynode/core/config/pynode.ini')
        eth_section = config['Ethereum']
        contract_section = config['Contracts']

        MainModel.eth_host = eth_section['remote']
        MainModel.pandora_abi_path = contract_section['abi_path']
        MainModel.pandora_contract_address = contract_section['pandora']
        MainModel.current_worker_contract = contract_section['worker_node']
    except Exception as ex:
        print("Error reading config: %s, exiting", type(ex))

    if results.remove_account is not 'False':
        MainModel.remove_flag = True

    print('Reading properties success')
    print('Eth host                    : ' + MainModel.eth_host)
    print('Pandora contract address    : ' + MainModel.pandora_contract_address)
    print('ABI path                    : ' + MainModel.pandora_abi_path)
    print('Action remove               : ' + str(MainModel.remove_flag))
    print('Current worker contract     : ' + MainModel.current_worker_contract)
    if results:
        MainModel.new_worker_account = results.new_worker_account
        if not MainModel.remove_flag:
            print('Provide worker contract for account : ' + MainModel.new_worker_account)
        else:
            print('========================= DESTROY =========================')
            print('Destroy worker contract for account : ' + MainModel.new_worker_account)
            print('Worker contract address             : ' + MainModel.current_worker_contract)
            print('========================= DESTROY =========================')
    else:
        print('Provide account address for creating worker contract (use -a (--account) parameter on tool launch)')
        return

    print('Try instantiate ABI')
    if init_abi_contract():
        print('ABI load success')
    process_create_worker_contract()
# -------------------------------------------------


# -------------------------------------------------
# read and store contract abi
# -------------------------------------------------
def init_abi_contract() -> bool:
    if os.path.isdir(MainModel.pandora_abi_path):
        if os.path.isfile(MainModel.pandora_abi_path + "Pandora.json"):
            with open(MainModel.pandora_abi_path + "Pandora.json", encoding='utf-8') as pandora_contract_file:
                MainModel.pandora_abi = json.load(pandora_contract_file)['abi']
                print('Pandora main contract ABI loaded success')
                return True
    else:
        print('ABI not found')
        return False
# -------------------------------------------------


# -------------------------------------------------
# main launcher
# -------------------------------------------------
if __name__ == "__main__":
    main(sys.argv)



