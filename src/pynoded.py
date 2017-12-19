import sys
import logging
import getopt
from getpass import getpass
from configparser import ConfigParser

from broker import Broker

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )


def run(config_file: str, password: str):
    logging.debug('Starting broker with config')

    logging.debug("Loading config file '%s'", config_file)
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
        broker = Broker(eth_server=eth_server, abi_path=eth_contracts['abi_path'],
                        pandora=eth_contracts['pandora'], node=eth_contracts['worker_node'],
                        vault=config['Account']['vault'],
                        use_hooks=eth_contracts.getboolean('hooks'))
    except Exception as ex:
        logging.error("Error reading config: %s, exiting", type(ex))
        logging.error(ex.args)
        return

    if password is None:
        password = getpass('Please provide password for unlocking private key: ')

    if broker.connect(password) is False:
        return

    # Remove the following line in order to put the app into a daemon mode (running on the background)
    broker.join()


def main(argv):
    conf_file = 'pynode.ini'
    password = None
    helpstring = 'pynoded -c <config_file> -p <password>'

    try:
        opts, args = getopt.getopt(argv[1:], "hc:p:", ["config=", "password="])
    except getopt.GetoptError:
        print(helpstring)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpstring)
            sys.exit()
        elif opt in ("-c", "--config"):
            conf_file = arg
        elif opt in ("-p", "--password"):
            password = arg

    run(config_file=conf_file, password=password)


if __name__ == "__main__":
    main(sys.argv)
