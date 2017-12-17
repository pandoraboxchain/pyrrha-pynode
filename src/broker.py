import logging
import time
from threading import Thread

from patterns.singleton import *
from connectors.eth_connector import EthConnector
from webapi.webapi import *


class Broker (Singleton, Thread):
    """
    Broker manages all underlying services/threads and arranges communications between them. Broker directly manages
    WebAPI and Ethereum threads and provides delegate interfaces for capturing their output via callback functions.
    This is done via implementing `EthDelegate` and `WebDelegate` abstract classes.
    """

    def __init__(self, eth_server: str, abi_path: str, pandora: str, node: str, use_hooks: bool = False):
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
        self.eth_server = eth_server
        self.abi_path = abi_path

        # Instantiating services objects
        self.pandora = EthConnector(server=self.eth_server, address=pandora,
                                    abi_path=self.abi_path, abi_file='PandoraHooks' if use_hooks else 'Pandora')
        self.node = EthConnector(server=self.eth_server, address=node, abi_path=self.abi_path, abi_file='WorkerNode')
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
            result &= self.pandora.connect()
            result &= self.pandora.init_contract() if result else False
            result &= self.node.connect() if result else False
            result &= self.node.init_contract() if result else False
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
