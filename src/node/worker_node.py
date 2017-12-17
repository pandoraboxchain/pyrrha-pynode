from connectors.eth_connector import EthConnector


class WorkerNode(EthConnector):

    def __init__(self, server: str, address: str, abi_path: str, abi_file: str):
        super().__init__(server, address, abi_path, abi_file)

    def bootstrap(self) -> bool:
        self.connect()
        self.init_contract()
        self.bind_event('StateChanged', self.__on_state_changed)
        self.event_filter.join()
        return True

    def __on_state_changed(self, event: dict):
        state_old = event['args']['oldState']
        state_new = event['args']['newDtate']
        self.logger.debug("Worker node changed its state from %s to %s", state_old, state_new)
        pass
