from eth.stateful_contract import *


class NodeActions(StatefulContract):

    def cognitive_job_address(self) -> str:
        address = self.contract.call().activeJob()
        if address is '0':
            address = None
        return address

    def transact_alive(self):
        self.logger.info('Sending alive status')
        pass

    def transact_accept_assignment(self):
        self.logger.info('Accepting assignment')
        self.transact('acceptAssignment', lambda tx: tx.acceptAssignment())

    def transact_process_to_data_validation(self):
        self.logger.info('Processing to data validation')
        self.transact('processToDataValidation', lambda tx: tx.processToDataValidation())

    def transact_accept_valid_data(self):
        self.logger.info('Confirming data validness')
        self.transact('acceptValidData', lambda tx: tx.acceptValidData())

    def transact_process_to_cognition(self):
        self.logger.info('Processing to cognitive work')
        self.transact('processToCognition', lambda tx: tx.processToCognition())

    def transact_provide_results(self, ipfs_file: str):
        self.logger.info('Providing results')
        self.transact('provideResults', lambda tx: tx.provideResults(ipfs_file))
