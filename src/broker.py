import logging
import traceback
from collections import namedtuple

from singleton import *
from eth import *
from webapi.webapi import *

# Configuration object designed in form of named tuple (common style for all configuration in the project).
# The reason of using named tuples instead of dict is to get compile-time errors in case of misspelled config keys.
BrokerConfig = namedtuple('BrokerConfig', 'eth webapi')

class Broker (Singleton, EthDelegate, WebDelegate):
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
        super().__init__()

        # Initializing logger object
        self.logger = logging.getLogger("broker")

        # Saving config
        self.config = config

        # Instantiating services objects
        # self.eth = Eth(config=self.config.eth, delegate=self)
        # self.api = WebAPI(config=self.config.webapi, delegate=self)

    def run(self) -> bool:
        """
        Starts all necessary interfaces (WebAPI, Ethereum and its underlying interfaces). Fails if any of them failed.

        :return: Success or failure status as a bool value
        """

        # Trying to bind web api port (to fail early before trying everything else more complex)
        self.logger.debug("Statring api...")
        if not self.api.bind():
            self.logger.error("Can't bind to Web API port, shutting down")
            return False

        # Now trying to connect Ethereum node JSON RPC interface
        self.logger.debug("API started successfully")
        self.logger.debug("Starting broker...")
        if not self.eth.bind():
            self.logger.error("Can't connect Ethereum network, shutting down")
            return False

        # Since all necessary network environments are available for now we can run the services as a separate threads
        self.api.run()
        self.eth.run()

        self.logger.debug("Broker started successfully")

        return True
