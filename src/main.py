import sys
import logging

from broker import Broker, BrokerConfig, EthConfig

CONFIGS_ETH = {
    'LOCAL': EthConfig(server='http://127.0.0.1', port=8545,
                       contract='0x33c9d18fb98e08fe73262e333bcbf428ebedbeff',
                       abi='../../abi', hooks=True),
    'GANACHE': EthConfig(server='http://127.0.0.1', port=7545,
                       contract='0x058f7ceff4a998e5ce3ce7a8e913e32e9fa52601',
                       abi='../../abi', hooks=True),
    'INFURA': EthConfig(server='https://ropsten.infura.io', port=443,
                        contract='0x058f7ceff4a998e5ce3ce7a8e913e32e9fa52601',
                        abi='../../abi', hooks=True),
}

#CONFIGS_IPFS = {
#    'LOCAL': IPFSConfig(server='127.0.0.1', port=5001, data_path='/tmp'),
#    'INFURA': IPFSConfig(server='https://ipfs.infura.io', port=5001, data_path='/tmp')
#}

CONFIGS = {
    'TEST_LOCAL': BrokerConfig(
        eth=CONFIGS_ETH['LOCAL']
    ),
    'TEST_GANACHE': BrokerConfig(
        eth=CONFIGS_ETH['GANACHE']
    ),
}

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )


def run(config_name):
    logging.debug('Starting broker with config %s...', config_name)
    broker = Broker(CONFIGS[config_name])
    broker.connect()
    # Remove the following line in order to put the app into a daemon mode (running on the background)
    broker.join()


def main(argv):
    run('TEST_GANACHE')


if __name__ == "__main__":
    main(sys.argv)
