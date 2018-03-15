from eth.stateful_contract import StatefulContract


class JobGetters(StatefulContract):

    def kernel_address(self) -> str:
        return self.contract.call().kernel()

    def dataset_address(self) -> str:
        return self.contract.call().dataset()

    def workers(self) -> [str]:
        workers = []
        workers_count = self.contract.call().activeWorkersCount()
        for w in range(0, workers_count):
            workers.append(self.contract.call().activeWorkers(w).lower())
        return workers
