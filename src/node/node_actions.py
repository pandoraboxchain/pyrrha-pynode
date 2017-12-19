from eth.stateful_contract import *


class NodeActions(StatefulContract):

    def transact_alive(self):
        self.logger.debug('Sending alive status')
        pass

    def transact_accept_assignment(self):
        self.logger.debug('Accepting assignment')
        self.transact('acceptAssignment', lambda tx: tx.acceptAssignment())

    def transact_process_to_data_validation(self):
        self.logger.debug('Processing to data validation')
        self.transact('processToDataValidation', lambda tx: tx.processToDataValidation())

    def transact_accept_valid_data(self):
        self.logger.debug('Confirming data validness')
        self.transact('acceptValidData', lambda tx: tx.acceptValidData())

    def transact_process_to_cognition(self):
        self.logger.debug('Processing to cognitive work')
        self.transact('processToCognition', lambda tx: tx.processToCognition())

    def transact_provide_results(self, ipfs_file: str):
        self.logger.debug('Providing results')
        self.transact('provideResults', lambda tx: tx.provideResults(''))
