from eth.stateful_contract import *


class NodeActions(StatefulContract):

    def transact_alive(self):
        self.logger.debug('Sending alive status')
        pass

    def transact_accept_assignment(self):
        self.logger.debug('Accepting assignment')
        pass

    def transact_process_to_data_validation(self):
        pass

    def transact_accept_valid_data(self):
        pass

    def transact_process_to_cognition(self):
        pass

    def transact_provide_results(self, ipfs_file: str):
        pass
