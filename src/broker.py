import logging
import time
from collections import namedtuple
from threading import Thread

from patterns.singleton import *
from connectors.eth_connector import EthConnector
from webapi.webapi import *

# Configuration objects designed in form of named tuple (common style for all configuration in the project).
# The reason of using named tuples instead of dict is to get compile-time errors in case of misspelled config keys.
BrokerConfig = namedtuple('BrokerConfig', 'eth')
EthConfig = namedtuple('EthConfig', 'server port contract abi hooks')


class Broker (Singleton, Thread):
    """
    Broker manages all underlying services/threads and arranges communications between them. Broker directly manages
    WebAPI and Ethereum threads and provides delegate interfaces for capturing their output via callback functions.
    This is done via implementing `EthDelegate` and `WebDelegate` abstract classes.
    """

    def __init__(self, config: BrokerConfig):
        """
        Instantiates Broker object and its members, but does not initiates them (network interfaces are not created/
        bind etc). Broker follows two-step initialization pattern (`Broker(...)` followed by `broker.run` call.

        :param config: Configuration named tuple `BrokerConfig` containing also configuration of all nested services
        (WebAPI, Ethereum connector)
        """

        # Calling singleton init preventing repeated class instantiation
        Singleton.__init__(self)
        Thread.__init__(self, daemon=True)

        # Initializing logger object
        self.logger = logging.getLogger("broker")

        # Saving config
        self.config = config

        # Instantiating services objects
        econf = self.config.eth
        self.eth = EthConnector(host=econf.server, port=econf.port, address=econf.contract,
                                abi_path=econf.abi, abi_file='PandoraHooks' if econf.hooks else 'Pandora')
        # self.api = WebAPI(config=self.config.webapi, delegate=self)

    def run(self) -> bool:
        time.sleep(1000000)

    def connect(self) -> bool:
        """
        Starts all necessary interfaces (WebAPI, Ethereum and its underlying interfaces). Fails if any of them failed.

        :return: Success or failure status as a bool value
        """

        # Trying to bind web api port (to fail early before trying everything else more complex)
        # self.logger.debug("Statring api...")
        # if not self.api.bind():
        #     self.logger.error("Can't bind to Web API port, shutting down")
        #     return False

        # Now trying to connect Ethereum node JSON RPC interface
        # self.logger.debug("API started successfully")
        # self.logger.debug("Starting broker...")
        # if not self.eth.bind():
        #     self.logger.error("Can't connect Ethereum network, shutting down")
        #     return False

        # Since all necessary network environments are available for now we can run the services as a separate threads
        # self.api.run()
        # self.eth.run()

        result = True
        try:
            result &= self.eth.connect()
            result &= self.eth.init_contract() if result else False
        except Exception as ex:
            self.logger.error("Exception connecting to Ethereum: %s", type(ex))
            self.logger.error(ex.args)
            return False
        if result is not True:
            self.logger.error("Unable to start broker, exiting")
            return False

        self.logger.debug("Broker started successfully")

        super().start()

        return True
