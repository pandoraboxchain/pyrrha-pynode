import numpy as np


class BaseCoreConfiguration:

    # abstract class that implement base configuration and logical methods
    # for config test case we can overload basic configuration of current abstract

    # HOOKS           0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe4
    # WORKER CONTRACT 0x5677db552d5fd9911a5560cb0bd40be90a70eff2
    # JOB IN WORKER   0xb9462ef3441346dbc6e49236edbb0df207db09b7
    # KERNEL          0x345ca3e014aaf5dca488057592ee47305d9b3e10
    # DATASET         0xf12b5dd4ead5f743c6baa640b0216200e89b60da

    pandora_hooks_address = "0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe4"
    worker_node_address   = "0x5677db552d5fd9911a5560cb0bd40be90a70eff2"
    cognitive_job_address = "0xb9462ef3441346dbc6e49236edbb0df207db09b7"
    kernel_address        = "0x345ca3e014aaf5dca488057592ee47305d9b3e10"
    dataset_address       = "0xf12b5dd4ead5f743c6baa640b0216200e89b60da"

    # default test accounts
    accounts = ["0x627306090abab3a6e1400e9345bc60c78a8bef57",
                "0xf17f52151ebef6c7334fad080c5704d77216b732",
                "0xc5fdf4076b8f3a5357c5e395ab970b5b54098fef"]

    # flag for emulate empty job address (0 = normal mode, 1 = empty address)
    empty_job_address = 0
    # flag for emulate wrong job address (0 = normal mode, 1 = wrong address)
    wrong_job_address = 0

    # worker node states
    # ------------------
    # OFFLINE                   = 1
    # IDLE                      = 2
    # ASSIGNED                  = 3
    # READY_FOR_DATA_VALIDATION = 4
    # VALIDATING_DATA           = 5
    # READY_FOR_COMPUTING       = 6
    # COMPUTING                 = 7
    # INSUFFICIENT_STAKE        = 8
    # UNDER_PENALTY             = 9
    worker_state = 3
    # flag that apply state change for worker
    worker_state_change = 0

    # cognitive jobs states
    # ---------------------
    # GATHERING_WORKERS    = 1
    # INSUFFICIENT_WORKERS = 2
    # DATA_VALIDATION      = 3
    # INVALID_DATA         = 4
    # COGNITION            = 5
    # PARTIAL_RESULT       = 6
    # COMPLETED            = 7
    job_state = 1
    # flag that apply state change for job
    job_state_change = 0

    # consider that we have deployed contracts
    # and at the moment some blocks are already added to the blockchain
    __default_block_number = 13

    # ethereum current syncing state (1 = syncing, 0 = normal state)
    eth_node_state = 0

    # method signature for calling contracts while initialize
    # example (pandora.init_contract(), node.init_contract(), job.init_contract())
    __call_contract_method_signature = "0x8da5cb5b"

    # method signature for getting current contracts state for WORKER and COGNITIVE_JOB
    __call_current_state_signature = "0x0c3f6acf"

    # method signature for getting job address from worker
    __call_job_address_signature = "0x8daeaa40"

    # filters for state change monitoring
    __filters = {}

    __instance = None

    def __init__(self):
        if BaseCoreConfiguration.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            BaseCoreConfiguration.__instance = self

    def set_default_values(self):
        self.pandora_hooks_address = "0x2c2b9c9a4a25e24b174f26114e8926a9f2128fe4"
        self.worker_node_address = "0x5677db552d5fd9911a5560cb0bd40be90a70eff2"
        self.cognitive_job_address = "0xb9462ef3441346dbc6e49236edbb0df207db09b7"
        self.kernel_address = "0x345ca3e014aaf5dca488057592ee47305d9b3e10"
        self.dataset_address = "0xf12b5dd4ead5f743c6baa640b0216200e89b60da"

        self.empty_job_address = 0

        self.accounts = ["0x627306090abab3a6e1400e9345bc60c78a8bef57",
                         "0xf17f52151ebef6c7334fad080c5704d77216b732",
                         "0xc5fdf4076b8f3a5357c5e395ab970b5b54098fef"]

        self.worker_state = 3
        self.worker_state_change = 0
        self.job_state = 1
        self.job_state_change = 0

        self.eth_node_state = 0

    @staticmethod
    def get_instance():
        """ Static access method. """
        if BaseCoreConfiguration.__instance is None:
            BaseCoreConfiguration()
        return BaseCoreConfiguration.__instance

    def get_core_syncing_state(self):
        if self.eth_node_state == 0:
            return False
        if self.eth_node_state == 1:
            return {
                "startingBlock": '0x384',
                "currentBlock": '0x386',
                "highestBlock": '0x454'
            }

    def eth_call(self, params: dict, latest: str):
        # initial contract calls
        if params['data'] == self.__call_contract_method_signature:
            # return different data on request to different contracts
            # call to PANDORA contract
            if params['to'] == self.pandora_hooks_address:
                # return call to pandora contract pandora.init_contract()
                return "0x000000000000000000000000627306090abab3a6e1400e9345bc60c78a8bef57"
            # call to WORKER contract
            elif params['to'] == self.worker_node_address:
                # return call to node (worker) node.init_contract()
                return "0x000000000000000000000000627306090abab3a6e1400e9345bc60c78a8bef57"
            # call to JOB contract
            elif params['to'] == self.cognitive_job_address:
                # return call to job.init_contract()
                return "0x0000000000000000000000002c2b9c9a4a25e24b174f26114e8926a9f2128fe4"
            # KERNEL address call
            elif params['to'] == self.kernel_address:
                return "0x000000000000000000000000627306090abab3a6e1400e9345bc60c78a8bef57"
            # DATASET address call
            elif params['to'] == self.dataset_address:
                return "0x000000000000000000000000627306090abab3a6e1400e9345bc60c78a8bef57"
            # else return empty
            else:
                return "0x0000000000000000000000000000000000000000"

        if params['data'] == self.__call_current_state_signature:
            # ask WORKER contract for current state
            if params['to'] == self.worker_node_address:
                return str("0x" + '{:0>64}'.format(self.worker_state))
            # ask COGNITIVE JOB contract for current state
            if params['to'] == self.cognitive_job_address:
                return str("0x" + '{:0>64}'.format(self.job_state))

        if params['data'] == self.__call_job_address_signature:  # get JOB address form WORKER
            if params['to'] == self.worker_node_address:         # call WORKER contract for job
                if self.empty_job_address == 1:                  # flag fo emulate empty job
                    # empty JOB address
                    return "0x0000000000000000000000000000000000000000000000000000000000000000"
                return "0x000000000000000000000000b9462ef3441346dbc6e49236edbb0df207db09b7"  # return JOB ACTUAL Address

        # TODO refactor data
        # call JOB to get parent WORKER Address
        if params['data'] == "0x589094000000000000000000000000000000000000000000000000000000000000000000":
            if params['to'] == "0xb9462ef3441346dbc6e49236edbb0df207db09b7":
                return "0x0000000000000000000000005677db552d5fd9911a5560cb0bd40be90a70eff2"  ### WORKER address
        # call JOB to get KERNEL address
        if params['data'] == "0xd4aae0c4":
            if params['to'] == "0xb9462ef3441346dbc6e49236edbb0df207db09b7":
                return "0x000000000000000000000000345ca3e014aaf5dca488057592ee47305d9b3e10"  ### KERNEL address
        # call JOB to get DATASET address
        if params['data'] == "0x02b728ab":
            if params['to'] == "0xb9462ef3441346dbc6e49236edbb0df207db09b7":
                return "0x000000000000000000000000f12b5dd4ead5f743c6baa640b0216200e89b60da"  ### DATASET address

        # call KERNEL and DATASET to get ipfs addresses
        if params['data'] == "0xe1b40a76":
            if params['to'] == "0x345ca3e014aaf5dca488057592ee47305d9b3e10":                 ### KERNEL address
                return "0x0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002e516d5a325468447971356a5a5347706e69554d673167624a507a476b34415342787a74764e5976617171364d7a5a000000000000000000000000000000000000"
            if params['to'] == "0xf12b5dd4ead5f743c6baa640b0216200e89b60da":                 ### DATASET address
                return "0x0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002e516d534664696b4b624843426e54524d677863616b6a4c51443545364e626d6f6f3639596251504d394143584a6a000000000000000000000000000000000000"

        # worker nodes count request
        if params['data'] == "0x4804b4ba":
            if params['to'] == "0xb9462ef3441346dbc6e49236edbb0df207db09b7":
                return "0x0000000000000000000000000000000000000000000000000000000000000001"

        if params['data'] == "0x589094000000000000000000000000000000000000000000000000000000000000000000":
            if params['to'] == "0xb9462ef3441346dbc6e49236edbb0df207db09b7":
                return "0x0000000000000000000000005677db552d5fd9911a5560cb0bd40be90a70eff2"

        return "0x0"

    def eth_new_filter(self, params: dict, **kwargs):
        if params['address'] == self.worker_node_address:
            self.__filters.update({'0x0a': self.worker_node_address})
            return "0x0a"
        if params['address'] == self.cognitive_job_address:
            self.__filters.update({"0x09": self.cognitive_job_address})
            return "0x09"

    def eth_get_filter_changes(self, params: dict, **kwargs):
        # not all variants are emulated
        if self.__filters[params] == self.worker_node_address:
            if self.worker_state_change == 0:
                return []
            if self.worker_state == 4:
                self.worker_state_change = 0
                return self.__compose_state_change_response(3, 4, self.worker_node_address)
            if self.worker_state == 2:
                self.worker_state_change = 0
                return self.__compose_state_change_response(4, 2, self.worker_node_address)
            if self.worker_state == 5:
                self.worker_state_change = 0
                return self.__compose_state_change_response(4, 5, self.worker_node_address)
        if self.__filters[params] == self.cognitive_job_address:
            if self.job_state_change == 0:
                return []
            if self.job_state == 3:
                self.job_state_change = 0
                return self.__compose_state_change_response(1, 3, self.cognitive_job_address)
            if self.job_state == 4:
                self.job_state_change = 0
                return self.__compose_state_change_response(3, 4, self.cognitive_job_address)

    def eth_get_accounts(self, *args, **kwargs):
        return self.accounts

    def eth_estimate_gas(self, params, **kwargs):
        # gas estimation for worker contract
        if params['to'] == self.worker_node_address:
            # for now return static value (in real network values will be different)
            return "0x1344f"

    def eth_block_number(self, *args, **kwargs):
        self.__default_block_number = self.__default_block_number + 1
        return "0x"+str(self.__default_block_number)

    def eth_get_block_by_number(self, params, **kwargs):
        # current response return mined block by its number
        # THIS IS ONLY EMULATION
        if "0x14" in params:
            return self.__compose_block_response(
                block_number="0x14",
                s_hash="0x350393321a18d0efc92f2c9a1c1a88830a72c56ba092e8bef8d905e8c658438a",
                parent_hash="0xa3516cf725cbc5b2eed0581735cc3b792b95b200c0b3b5c4255d48e735c074b2",
                state_root="0xb53fbc8ee01bfdfbaf3edb40b384cad1977d2477b3981572cbd8498f433ef473",
                gas_used="0x7a48",
                timestamp="0x5a7d9168",
                transactions="0x7a59edcfd0b3476a3b270ab81d42a054e027f15f0038dc2f0e5d542b00e4a8c1")
        if "0x15" in params:
            return self.__compose_block_response(
                block_number="0x15",
                s_hash="0x975de4ff9caa944ef9937d690845ca1e851dc85f8ede4f152c7c507029e9f0cf",
                parent_hash="0x350393321a18d0efc92f2c9a1c1a88830a72c56ba092e8bef8d905e8c658438a",
                state_root="0x5a118062d3aaa1551675fa7419429fa7fee15c6e954ecb6188f9cb8eb3e3fbdc",
                gas_used="0x01344f",
                timestamp="0x5a7d921a",
                transactions="0xeb14f770f2894a9fc210b6c5a7f3f26bb059e9a7bbbf7813f2bf43f1094bddb6")
        if "0x16" in params:
            return self.__compose_block_response(
                block_number="0x16",
                s_hash="0x19f91daf0a31eee0a898896ddadfaa1255bfeacd3e46d9c5251d64a6b26503e3",
                parent_hash="0x975de4ff9caa944ef9937d690845ca1e851dc85f8ede4f152c7c507029e9f0cf",
                state_root="0xd2a23ee1239b56b93fa7daeca3b851fef1ae045811c2846f1f48b24fa63a34a0",
                gas_used="0x84f0",
                timestamp="0x5a7d94aa",
                transactions="0x7b10aa82be90d5c9e0eb12b3b3bfbc00695d643014d3db81d498d5c24f682cf1")
        if "0x17" in params:
            return self.__compose_block_response(
                block_number="0x17",
                s_hash="0xd8409d95de2559fc4700572aea8883dcb9ee6b2fd9a45a6af3efa7419dd1ef42",
                parent_hash="0x19f91daf0a31eee0a898896ddadfaa1255bfeacd3e46d9c5251d64a6b26503e3",
                state_root="0xd2a23ee1239b56b93fa7daeca3b851fef1ae045811c2846f1f48b24fa63a34a0",
                gas_used="0x013d89",
                timestamp="0x5a7d960b",
                transactions="0x151191c6cee961cb4437ce5f16f0fac79d3d3ad3cc5f9cc1350d85dcf43a0790")
        if "0x18" in params:
            return self.__compose_block_response(
                block_number="0x18",
                s_hash="0x64f4f1788b7c9b36faa91d03f1faaf8f4bf0851513cece67c5a7006489cf9125",
                parent_hash="0xd8409d95de2559fc4700572aea8883dcb9ee6b2fd9a45a6af3efa7419dd1ef42",
                state_root="0x41263ba3c8e36d8c5dba8e8be5dd22e04a8333f9369139fb9db82916e0e66b3f",
                gas_used="0x83a6",
                timestamp="0x5a7d9730",
                transactions="0x38a150b35749727a9029cadc3cd6bc9738390f4f36fb6cff0bbae2090c65a431")

    # TODO add state transfer validation
    def eth_send_transaction(self, params: dict, **kwargs):
        # to WORKER contract
        if params['to'] == self.worker_node_address:
            if params['data'] == "0xdf12e6c3":
                # from 3 change state to 4 ASSIGNED => READY_FOR_DATA_VALIDATION
                # change job state from 1 to 3 GATHERING_WORKERS => DATA_VALIDATION
                self.worker_state = 4
                self.worker_state_change = 1
                self.job_state = 3
                self.job_state_change = 1
                # return transaction hash
                return "0xeb14f770f2894a9fc210b6c5a7f3f26bb059e9a7bbbf7813f2bf43f1094bddb6"
            if params['data'] == "0x77c6cc38":
                # change state to 5 = VALIDATING_DATA
                self.worker_state = 5
                self.worker_state_change = 1
                return "0x7b10aa82be90d5c9e0eb12b3b3bfbc00695d643014d3db81d498d5c24f682cf1"
            if params['data'] == "0x47850cce":
                # report invalid data
                # change job state from DATA_VALIDATION to INVALID_DATA
                # change worker state from VALIDATING_DATA to IDLE
                self.worker_state = 2
                self.worker_state_change = 1
                self.job_state = 4
                self.job_state_change = 1
                return "0x8a6a014986ce08943630d8e67f21ef6292e6b8f5fe0ff7c4fc2825869a1402dc"
            if params['data'] == "0x5e903db0":
                # change state to 6 = READY_FOR_COMPUTING
                self.worker_state = 6
                return "0x151191c6cee961cb4437ce5f16f0fac79d3d3ad3cc5f9cc1350d85dcf43a0790"
            if params['data'] == "0x06401ff4":
                # change state to 7 = COMPUTING
                self.worker_state = 7
                return "0x38a150b35749727a9029cadc3cd6bc9738390f4f36fb6cff0bbae2090c65a431"
            if len(params['data']) > 20: # data contain calculated result
                # change state to 2 = IDLE
                self.worker_state = 2
                return "0x14f8ebf65e18ca14f8ffc0905088429349d056960b48125c1e073f8e0a60c708"

    @staticmethod
    def __compose_state_change_response(from_state: int, to_state: int, address: str):
        return [{"logIndex": "0x00",
                 "transactionIndex": "0x00",
                 "transactionHash": "0x13483a4a8f9131622c736cc722fe7ac3de5135b702c30ea9af9fe9b966440295",
                 "blockHash": "0x5c5ff8f6de4257e6de9ac58b17df4b1c721a28030be0e432b0855fae790d184b",
                 "blockNumber": "0x15",
                 "address": address,
                 "data": str("0x" + '{:0>64}'.format(from_state) + '{:0>64}'.format(to_state)),
                 "topics": ["0xe8a97ea87e4388fa22d496b95a8ed5ced6717f49790318de2b928aaf37a021d8"],
                 "type": "mined"}]

    @staticmethod
    def __compose_block_response(block_number: str, s_hash: str, parent_hash: str,
                                 state_root: str, gas_used: str, timestamp: str, transactions: str):
        return {"number": block_number,
                "hash": s_hash,
                "parentHash": parent_hash,
                "nonce": "0x0",
                "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
                "logsBloom": "0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                             "00000000040000000000000000000020000000000000000000000000000000000000000400000000000000000"
                             "00000000000000000000000000000000000000000080000000000000000000000000000000000000000000000"
                             "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000001"
                             "00000000000000000000000000000000000000000000000000000000000000000000000000100000000000000"
                             "000000000000000000000000000000000000000000000000000000000000000000000",
                "transactionsRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
                "stateRoot": state_root,
                "receiptsRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
                "miner": "0x0000000000000000000000000000000000000000",
                "difficulty": "0x0",
                "totalDifficulty": "0x0",
                "extraData": "0x0",
                "size": "0x03e8",
                "gasLimit": "0x6691b7",
                "gasUsed": gas_used,
                "timestamp": timestamp,
                "transactions": [
                    transactions
                ],
                "uncles": []}


