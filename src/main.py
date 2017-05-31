import sys

from broker import Broker, BrokerConfig, IPFSConfig, MWAPIConfig
from eth_connector import EthConfig


CONFIGS = {
    'TEST_INFRA': BrokerConfig(
        mwapi=MWAPIConfig(host='[::]', port=50051, max_conns=10),
        ipfs=IPFSConfig(server='ipfs.infura.io', port=5001),
        eth=EthConfig(server='https://ropsten.infura.io', port=441, contract=''),
        max_tasks=10,
        ver_ma=0,
        ver_mi=1,
        patch=0,
        agent='neurowrk-test'
    )
}

def main(argv):
    print('Starting broker...')
    broker = Broker(CONFIGS['TEST_INFRA'])
    broker.run()
    print('Broker started successfully')

if __name__ == "__main__":
    main(sys.argv)
