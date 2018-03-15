import json
from eth.eth_connector import *
from ipfs.ipfs_connector import IPFSConnector


class Entity(EthConnector):

    def __init__(self, ipfs_api: IPFSConnector, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ipfs_api = ipfs_api
        self.json_info = None

    def init_contract(self) -> bool:
        if super().init_contract() is not True:
            return False

        try:
            ipfs_address = self.contract.call().ipfsAddress()
        except Exception as ex:
            self.logger.error("Exception initializing entities contract")
            self.logger.error(ex.args)
            return False

        self.logger.info("Downloading and reading JSON entities file %s...", ipfs_address)
        try:
            self.json_info = self.__read_json(ipfs_address)
        except Exception as ex:
            self.logger.error("Exception reading JSON entities file: %s", type(ex))
            self.logger.error(ex.args)
            return False
        self.logger.info("Entity file downloaded and parsed successfully")

        return True

    def __read_json(self, ipfs_address: str) -> dict:
        self.ipfs_api.download_file(ipfs_address)
        with open(ipfs_address) as json_file:
            info = json.load(json_file)
        return info
