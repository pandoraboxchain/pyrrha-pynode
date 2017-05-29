import sys

from .broker import *


def main(argv):
    broker = Broker()
    broker.run()

if __name__ == "__main__":
    main(sys.argv)
