import sys

from broker import Broker, BrokerConfig, IPFSConfig, MWAPIConfig
from eth_connector import EthConfig

CONFIGS_MWAPI = {
    'LOCAL': MWAPIConfig(host='[::]', port=50051, max_conns=10)
}

CONFIGS_ETH = {
    'LOCAL': EthConfig(server='http://127.0.0.1', port=8545, contract='0x33c9d18fb98e08fe73262e333bcbf428ebedbeff'),
    'INFURA': EthConfig(server='https://ropsten.infura.io', port=443, contract='')
}

CONFIGS_IPFS = {
    'LOCAL': IPFSConfig(server='127.0.0.1', port=5001, data_path='/tmp'),
    'INFURA': IPFSConfig(server='https://ipfs.infura.io', port=5001, data_path='/tmp')
}

CONFIGS = {
    'TEST_INFRA': BrokerConfig(
        mwapi=CONFIGS_MWAPI['LOCAL'],
        ipfs=CONFIGS_IPFS['LOCAL'],
        eth=CONFIGS_ETH['LOCAL'],
        max_tasks=10,
        ver_ma=0,
        ver_mi=1,
        patch=0,
        agent='neurowrk-test'
    )
}


def run(config_name):
    print('Starting broker with config %s...' % config_name)
    broker = Broker(CONFIGS[config_name])
    broker.run()


def main(argv):
    run('TEST_INFRA')

if __name__ == "__main__":
    main(sys.argv)
