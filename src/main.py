import sys
import logging
from configparser import ConfigParser

from broker import Broker

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )


def run(config_file: str):
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
    run('pynode.ini')


if __name__ == "__main__":
    main(sys.argv)
