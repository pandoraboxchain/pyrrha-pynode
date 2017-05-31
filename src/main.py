import sys

from broker import *


def main(argv):
    print('Starting broker...')
    broker = Broker()
    broker.run()
    print('Broker started successfully')

if __name__ == "__main__":
    main(sys.argv)
