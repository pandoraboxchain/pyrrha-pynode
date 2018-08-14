import time
import logging

from abc import ABCMeta, abstractmethod
from core.node.worker_node import WorkerNode
from threading import Thread
from core.patterns.pynode_logger import LogSocketHandler


class WorkerNodeStateDelegate(metaclass=ABCMeta):
    @abstractmethod
    def on_worker_node_state_change(self, event: dict):
        pass


class WorkerNodeStateMachineThread:

    def __init__(self, contract_container, delegate, address, contract, state_delegate: WorkerNodeStateDelegate):
        # Initializing logger object
        self.logger = logging.getLogger("WorkerNodeStateMachineThread")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(LogSocketHandler.get_instance())

        # init worker node
        self.worker_node = WorkerNode(contract_container=contract_container,
                                      delegate=delegate,
                                      address=address,
                                      contract=contract)

        # int filter and filter thread
        self.state_delegate = state_delegate
        self.worker_node_container = contract_container
        self.current_block_number = None

        self.filter_on_worker = contract_container.events.StateChanged.createFilter(fromBlock='latest')
        self.worker_node_event_thread = Thread(target=self.worker_filter_thread_loop, daemon=True)
        if not self.worker_node_event_thread.is_alive():
            self.worker_node_event_thread.start()

    # -------------------------------------
    # thread methods
    # -------------------------------------
    def get_worker_node_event_thread(self):
        return self.worker_node_event_thread

    def alive(self):
        return self.worker_node_event_thread.is_alive()

    # -------------------------------------
    # state methods
    # -------------------------------------
    def process_state(self):
        return self.worker_node.process_state()

    def state_table(self):
        return self.worker_node.state_table

    def state(self, new_state):
        self.worker_node.state = new_state

    # -------------------------------------
    # thread methods
    # -------------------------------------
    def worker_filter_thread_loop(self):
        past_block = self.worker_node_container.web3.eth.getBlock('latest')
        past_block_number = past_block.number
        last_call_time = 0
        while True:
            poll_interval, past_block, past_block_number = \
                self.calculate_thread_sleep_interval(past_block=past_block, past_block_number=past_block_number)
            try:
                if last_call_time + 60 < time.time():
                    self.logger.info('work_filter recreated on object timeout')
                    self.filter_on_worker = self.worker_node_container.events.StateChanged.createFilter(
                        fromBlock=self.current_block_number - 2)
                if self.filter_on_worker:
                    events = self.filter_on_worker.get_new_entries()
                    for event in events:
                        # validate current state and worker node address
                        current_state = self.worker_node.state
                        new_state = event['args']['newState']
                        if current_state != new_state:
                            self.state_delegate.on_worker_node_state_change(event)
                    last_call_time = time.time()
                else:
                    self.logger.info('work_filter recreated on object null')
                    self.filter_on_worker = self.worker_node_container.events.StateChanged.createFilter(
                        fromBlock=self.current_block_number - 2)
            except Exception as ex:
                self.logger.info('FILTER EXCEPTION ' + str(ex.args))
                self.logger.info('work_filter recreated')
                self.filter_on_worker = self.worker_node_container.events.StateChanged.createFilter(
                    fromBlock=self.current_block_number - 2)
                self.process_state()
            time.sleep(poll_interval)

    def calculate_thread_sleep_interval(self, past_block, past_block_number):
        # calculate sleep thread time
        current_block = self.worker_node_container.web3.eth.getBlock('latest')
        self.current_block_number = current_block.number
        diff = self.current_block_number - past_block_number
        if diff >= 1:
            dynamic_poll_interval = current_block.timestamp - past_block.timestamp
            poll_interval = dynamic_poll_interval / diff - 0.5
            self.logger.info('POLL_INTERVAL : ' + str(dynamic_poll_interval) +
                             ' sleep_time : ' + str(poll_interval) +
                             ' block_number : ' + str(self.current_block_number))
            past_block = self.worker_node_container.web3.eth.getBlock('latest')
            past_block_number = past_block.number
            return poll_interval, past_block, past_block_number
        else:
            return 5, past_block, past_block_number




