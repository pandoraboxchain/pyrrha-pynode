import sys
import logging
import getopt
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
        broker = Broker(eth_server=eth_server, abi_path=eth_contracts['abi_path'],
                        pandora=eth_contracts['pandora'], node=eth_contracts['worker_node'],
                        vault=config['Account']['vault'], data_dir=ipfs_section['store_in'],
                        ipfs_server=ipfs_use['server'], ipfs_port=int(ipfs_use['port']),
                        use_hooks=eth_contracts.getboolean('hooks'))
    except Exception as ex:
        logging.error("Error reading config: %s, exiting", type(ex))
        logging.error(ex.args)
        return

    if broker.connect() is False:
        return

    # Remove the following line in order to put the app into a daemon mode (running on the background)
    broker.join()


def main(argv):
    """Parses command-line options and evokes `run`"""

    conf_file = 'pynode.ini'
    password = None

    try:
        opts, args = getopt.getopt(argv[1:], "hc:p:", ["config="])
    except getopt.GetoptError:
        print(HELP)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(HELP)
            sys.exit()
        elif opt in ("-c", "--config"):
            conf_file = arg

    run(config_file=conf_file)


if __name__ == "__main__":
    main(sys.argv)
