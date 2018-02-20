import sys
import logging
import getopt
import os
import unittest

from configparser import ConfigParser
from broker import Broker

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )

HELP = """pynoded: Python version of Pandora Boxchain worker node daemon made for Pyrrha release
Version 0.9.0

Usage:
$ pynoded -c <config_file>
"""

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

# uncomment for
# use_env_cfg()

def run(config_file: str):
    """Reads config file, initializes configuration and creates Broker object that runs in a separate thread"""
    logging.info('Starting broker with config')
    logging.info("Loading config file '%s'", config_file)
    try:
        config = ConfigParser()
        config.read(config_file)
    except Exception as ex:
        logging.error("Error reading config: %s, exiting", type(ex))
        logging.error(ex.args)
        return
    try:
        eth_section = config['Ethereum']
        eth_contracts = config['Contracts']
        eth_use = eth_section['use']
        eth_server = eth_section[eth_use]
        ipfs_section = config['IPFS']
        ipfs_use = config['IPFS.%s' % ipfs_section['use']]
        broker = Broker(eth_server=eth_server,
                        abi_path=eth_contracts['abi_path'],
                        pandora=eth_contracts['pandora'],
                        node=eth_contracts['worker_node'],
                        data_dir=ipfs_section['store_in'],
                        ipfs_server=ipfs_use['server'],
                        ipfs_port=int(ipfs_use['port']),
                        use_hooks=eth_contracts.getboolean('hooks'))
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
    
    conf_file = '../pynode.ini'

    try:
        opts, args = getopt.getopt(argv[1:], "hc:p:", ["test", "config="])
    except getopt.GetoptError:
        print(HELP)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(HELP)
            sys.exit()
        elif opt in ("-c", "--config"):
            conf_file = arg
        elif opt in ("-t", "--test"):
            run_tests()
            return

    run(config_file=conf_file)


if __name__ == "__main__":
    main(sys.argv)
