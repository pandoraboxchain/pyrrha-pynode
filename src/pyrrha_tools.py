#! /usr/bin/env python3

import sys
import getopt

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

    if command is None:
        halt(1)
    else:
        print('Unknown command %s\n' % command)
        halt(1)


if __name__ == "__main__":
    main(sys.argv)
