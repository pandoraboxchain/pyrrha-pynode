

# throws while contracts cannot be instantiated
class ContractsAbiNotFound(Exception):
    pass


# throws on eth_connector while transaction excepts
class CriticalTransactionError(Exception):
    pass


# throws while web3 is not initialized
class NotInitialized(Exception):
    pass


# throws while pynode unable to connect configured eth_connector address
class EthConnectionException(Exception):
    pass


# throws while eth_connector node is currently not in sync
class EthIsNotInSyncException(Exception):
    pass


# throws while eth_connector connector try to obtain contract from blockchain
class ErrorContractGettingException(Exception):
    pass


# throws while unable init contracts
class WrongContractAddressOrABI(Exception):
    pass


# throws while JOB in worker are empty
class EmptyCognitiveJobInWorkerContract(Exception):
    pass


class ModelInconsistencyError (Exception):
    pass


class DataInconsistencyError (Exception):
    pass

