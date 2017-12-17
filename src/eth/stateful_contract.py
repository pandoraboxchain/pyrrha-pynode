from eth.eth_connector import EthConnector


class StatefulContract(EthConnector):

    def bootstrap(self) -> bool:
        self.connect()
        self.init_contract()
        self.__process_state()
        self.bind_event('StateChanged', self.__on_state_changed)
        self.event_filter.join()
        return True

    def __process_state(self):
        state = self.contract.call().currentState()
        self.logger.debug("Contract %s initial state is %s", self.abi_file, state)

    def __on_state_changed(self, event: dict):
        state_old = event['args']['oldState']
        state_new = event['args']['newDtate']
        self.logger.debug("Contract %s changed its state from %s to %s", self.abi_file, state_old, state_new)
        pass
