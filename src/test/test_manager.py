import logging
import threading
import sys

from manager import Manager
from broker import Broker
from test.core.base_test_core import BaseCoreConfiguration
from test.core.base_test_listener import BaseTestListener
from configparser import ConfigParser

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(levelname)s: %(message)s',
                    )


class TestManager:

    host = None
    test_listener = None
    test_listener_thread = None
    test_core_configuration = None

    # on init read configuration for running tests
    def __init__(self, *config_file):
        if len(config_file) == 0:
            # for launch all test by console
            config_file = '../pynode.ini'
        logging.info('Init test manager with %s config file', config_file)
        try:
            config = ConfigParser()
            config.read(config_file)
            main_section = config['TEST']
            self.host = main_section['host']
        except Exception as ex:
            logging.error("Error reading test config: %s, exiting", type(ex))
            logging.error(ex.args)
            return

    def get_test_listener_host(self) -> str:
        return self.host

    def get_configuration(self) -> BaseCoreConfiguration:
        self.test_core_configuration = BaseCoreConfiguration.get_instance()
        return self.test_core_configuration

    def run_test_listener(self, demon: bool = False):
        # run test listener in new daemon thread
        print("Launch mok eth listener on host : " + self.host)
        self.test_listener = BaseTestListener(host=self.host, configuration=self.test_core_configuration)
        self.test_listener_thread = threading.Thread(target=self.test_listener.launch)
        if demon:
            self.test_listener_thread.daemon = True
        self.test_listener_thread.start()
        print('Listener started in demon mode : ' + str(demon))

    @staticmethod
    def run_test_pynode(*config_file) -> int:
        if len(config_file) == 0:
            # for launch all test by console
            config_file = '../pynode.ini'
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
            test_section = config['TEST']
            eth_contracts = config['Contracts']
            ipfs_section = config['IPFS']
            host = test_section['host']
            ipfs_use = config['IPFS.%s' % ipfs_section['use']]

            Manager.get_instance().launch_mode = 1

            broker = Broker(eth_server=host,
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
            raise

        if broker.connect() is False:
            return

        broker.join()
        return 1


def launch_moc_service(*args):
    manager = TestManager('../../pynode.ini')
    manager.get_configuration().set_default_values()
    manager.run_test_listener()


if __name__ == "__main__":
    launch_moc_service(sys.argv)


