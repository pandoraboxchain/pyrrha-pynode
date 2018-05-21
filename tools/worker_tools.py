import sys
import os
import argparse
import json
import time

from configparser import ConfigParser
from web3 import Web3, HTTPProvider
from typing import Callable

from pathlib import Path
from hashlib import md5
from base64 import b64encode
from Crypto import Random
from Crypto.Cipher import AES


# -------------------------------------------------
# Main model for data storing
# -------------------------------------------------
class MainModel:
    eth_host = None
    pandora_contract_address = None
    pandora_abi_path = None
    pandora_abi = None
    remove_flag = False

    new_worker_account = None
    new_worker_account_p_key = None
    obtaining_flag = False
# -------------------------------------------------


# -------------------------------------------------
# main process for worker contract creation
# -------------------------------------------------
def process_create_worker_contract():
    # init connection and pandora contract
    connector = Web3(HTTPProvider(MainModel.eth_host))
    try:
        synk_info = connector.eth.syncing
    except Exception as ex:
        print('Unable to connect to eth node')
        raise Exception('Unable to connect to eth node')
    if synk_info is not False:
        print('Eth node in synking mode, try later')
        raise Exception('Eth node in synking mode, try later')

    print('Connection success, check provided customer account address')
    contract = connector.eth.contract(address=MainModel.pandora_contract_address,
                                      abi=MainModel.pandora_abi)
    # check currently provided accounts
    accounts = connector.eth.accounts
    print('Current accounts list')
    print(accounts)
    # check provided account for imported
    if MainModel.new_worker_account in accounts:
        # unlock account for create worker contract request
        local_password = obtain_local_password()
        unlock_result = unlock_account(connector, MainModel.new_worker_account, local_password)
        print('Unlock result : ' + str(unlock_result))
        if unlock_result is False:
            print('Unable to unlock account. Exiting')
            return
        print('Owner account ready for transactions')
    else:
        # provide import and unlocking
        local_password = obtain_local_password()
        print('Local password obtained, try to unlock account')
        if unlock_account(connector, MainModel.new_worker_account, local_password):
            print('Account unlocked success')
        else:
            print('Account unlock fail, try to import account and than unlock')
            if import_account(connector, MainModel.new_worker_account_p_key, local_password):
                print('Account import success')
                print('Try to unlock')
                unlock_result = unlock_account(connector, MainModel.new_worker_account, local_password)
                print('Unlock result : ' + str(unlock_result))
            else:
                print("Owner account unlock fail.")
                return
            print('Owner account ready for transactions')

    # for provide possibility use current created worker node contract with vault
    # provide vault recreation before account balance validation
    vault_result = create_vault(local_password, MainModel.new_worker_account)
    if not vault_result:
        print('Unable to create vault.')
        return

    account_balance = connector.eth.getBalance(MainModel.new_worker_account)
    if account_balance < 4000000000000000000:
        print('For creating worker node account your need to spend 3 ETH and 1 ETH need for management node sates')
        print('If your currently create worker node contract, you can try start pynode with current configuration')
        print('Unable to create worker contract. Exit.')
        return

    event = contract.on('WorkerNodeCreated')
    event.start()
    event.watch(on_worker_node_created)
    print('Event listener for worker node creation startup success')

    if MainModel.remove_flag is False:
        print('Transact for creation worker node contract')
        try:
            tx_result_hash = transact(contract,
                                      lambda tx: tx.createWorkerNode(),
                                      MainModel.new_worker_account)
            print('transaction details : ' + tx_result_hash)
            while MainModel.obtaining_flag is False:
                time.sleep(3)
        except Exception as ex:
            print('Exception while transact creation worker contract')
            print(ex.args)
            return
    else:
        print('Transact for destroy worker node contract')
        try:
            tx_result_hash = transact(contract,
                                      lambda tx: tx.destroyWorkerNode(),
                                      MainModel.new_worker_account)
            print('transaction details : ' + tx_result_hash)
            while MainModel.obtaining_flag is False:
                time.sleep(3)
        except Exception as ex:
            print('Exception while transact destroy worker contract')
            print(ex.args)
            return


def on_worker_node_created(event: dict):
    try:
        address = event['args']['workerNode']
        print("Node creation success address : %s", address)
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
    print("Pynode is configured and ready for launch with default parameters")
    MainModel.obtaining_flag = True
# -------------------------------------------------


# -------------------------------------------------
# Transactional methods
# -------------------------------------------------
def transact(contract, cb: Callable, address):
    tx = contract.transact({'from': address})
    return cb(tx)
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


def import_account(connector, account_private_key, password) -> bool:
    result = True
    try:
        result = connector.personal.importRawKey(account_private_key, password)
    except Exception:
        print('Account already imported. Continue operation.')
    return result


def unlock_account(connector, account, password) -> bool:
    try:
        unlock = connector.personal.unlockAccount(account=account,
                                                  passphrase=password,
                                                  duration=10)  # duration - seconds
    except Exception as ex:
        print('Exception while account unlock processing')
        print(ex.args)
        return False
    return unlock


def create_vault(local_password: str, new_worker_account: str) -> bool:
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
        vault_password = md5(new_worker_account.encode('utf8')).hexdigest()
        raw = pad(local_password + "_" + MainModel.new_worker_account_p_key).encode('utf8')
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
                -p (--private_key) - use this flag to provide worker node account private key
                -r (--remove) - use this flag to destroy worker node contract for your account
            example >python ./worker_tools.py -a <owner_account_address> -p <account_private_key>    
                                  
            Current tool try to import your account and ask for local password, password for account
            will be stored in secured vault and will be used on node start. This password is only actual 
            for pandora ethereum node
            
            NOTE: Current version using private node module for account manipulation that is why you will be
            asked for private local password on account importing and unlocking. Those password is stores on 
            pandora ethereum node.
            
            WARNING: The current configuration works with private module which is set 
            when you start your Ethereum node.  
            To work without this module code improvements and testing are needed!
            
            WARNING: Current operation will overwrites your key vault, please back up your vault and pynode 
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
    parser.add_argument('-p',
                        '--private_key',
                        action="store",
                        dest='worker_account_private_key',
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
    except Exception as ex:
        print("Error reading config: %s, exiting", type(ex))

    if results.remove_account is not 'False':
        MainModel.remove_flag = True

    print('Reading properties success')
    print('Eth host                    : ' + MainModel.eth_host)
    print('Pandora contract address    : ' + MainModel.pandora_contract_address)
    print('ABI path                    : ' + MainModel.pandora_abi_path)
    print('Action remove               : ' + str(MainModel.remove_flag))
    if results:
        MainModel.new_worker_account = results.new_worker_account
        MainModel.new_worker_account_p_key = results.worker_account_private_key
        print('Provide worker contract for account : ' + MainModel.new_worker_account)
        print('With private key                    : ' + MainModel.new_worker_account_p_key)
    else:
        print('Provide account address for creating worker contract (use -a (--account) parameter on tool launch)')
        return

    print('Try instantiate ABI')
    if init_abi_contract():
        print('ABI load success')
    process_create_worker_contract()
# -------------------------------------------------


# -------------------------------------
# read and store contract abi
# -------------------------------------
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


# -------------------------------------
# main launcher
# -------------------------------------
if __name__ == "__main__":
    main(sys.argv)



