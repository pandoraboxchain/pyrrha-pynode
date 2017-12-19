#! /usr/bin/env python3

import sys
import logging
import getopt
from web3 import Web3
# from eth_tester import EthereumTester
# from web3.providers.eth_tester import EthereumTesterProvider
from getpass import getpass
from scrypt import decrypt, encrypt


HELPSTRING = '''Set of pyrrha network worker node useful tools

Usage:
$ pyrrha-tools command

Commands and options:

encrypt-account -f <file_to_save>
    Asks for a private key, password and saves an encrypted Web3 account to the specified file
decrypt-account -f <account_file>
    Asks for a password, reads file and tries to decrypt it, printing account JSON to STDOUT
'''


def halt(code: int = 2):
    print(HELPSTRING)
    sys.exit(code)


def encrypt_account(filename: str):
    password = getpass('Password: ')
    pri_key = getpass('Private key: ')
    cypher = encrypt(pri_key, password)
    with open(filename, 'wb') as file:
        file.write(cypher)


def decrypt_account(filename: str):
    password = getpass('Password: ')
    with open(filename, 'rb') as file:
        cypher = file.read()
    pri_key = decrypt(cypher, password)
    print('Private key: %s' % pri_key)


def get_file_option(opts) -> str:
    file = None
    for opt, arg in opts:
        if opt in ("-f", "--file"):
            file = arg

    if file is None:
        print('No file provided, run with -h option for command details\n')
        sys.exit(1)

    return file


def main(argv):
    # eth_tester = EthereumTester()
    # web3 = Web3(EthereumTesterProvider(eth_tester))

    try:
        command, argv = argv[1], argv[2:]
        opts, args = getopt.getopt(argv, "hf:", ["file="])
    except Exception:
        return halt()

    if command == 'encrypt-account':
        file = get_file_option(opts)
        encrypt_account(file)
    elif command == 'decrypt-account':
        file = get_file_option(opts)
        decrypt_account(file)
    elif command is None:
        halt(1)
    else:
        print('Unknown command %s\n' % command)
        halt(1)


if __name__ == "__main__":
    main(sys.argv)
