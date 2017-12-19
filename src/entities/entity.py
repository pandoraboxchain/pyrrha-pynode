from eth.eth_connector import *
from ipfs.ipfs_connector import IPFSConnector


class Entity(EthConnector):

    def __init__(self, ipfs_api: IPFSConnector, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ipfs_api = ipfs_api
        self.__info = None

    def init_contract(self) -> bool:
        if super().init_contract() is not True:
            return False

        try:
            ipfs_address = self.contract.call().ipfsAddress()
        except Exception as ex:
            self.logger.error("Exception initializing entity contract", type(ex))
            self.logger.error(ex.args)
            return False

        self.logger.info("Downloading and reading JSON entity file %s...", ipfs_address)
        try:
            self.__info = self.__read_json(ipfs_address)
        except Exception as ex:
            self.logger.error("Exception reading JSON entity file: %s", type(ex))
            self.logger.error(ex.args)
            return False
        self.logger.info("Entity file downloaded and parsed successfully")

        return True

    def __read_json(self, ipfs_address: str) -> dict:
        self.__ipfs_api.download_file(ipfs_address)
        with open(ipfs_address) as json_file:
            info = json.load(json_file)
        return info
