import socket
import threading

from logging import LogRecord
from webapi.web_api_models import ClassApiSerializer, PynodeStatus, PynodeLogRecord
from webapi.web_socket_handler import WebSocketHandler


class WebSocket(threading.Thread):

    __instance = None

    tcp_socket = None
    tcp_socket_address = None
    tcp_socket_handler = None
    tcp_socket_connections = None

    client = None
    address = None

# ---------------------------------
# base socket listener, completed as singleton
# ---------------------------------
    # listener is singleton
    @staticmethod
    def get_instance():
        if WebSocket.__instance is None:
            # if no listener instance startup listener by default params
            WebSocket('localhost', 9090, 1)
        return WebSocket.__instance

    # base class for init and launch socket thread for monitoring pynode states
    def __init__(self, socket_host: str, socket_port: int, socket_clients: int):
        # start listener once and save instance for handle usage
        if WebSocket.__instance is None:
            self.tcp_socket_address = (str(socket_host), int(socket_port))
            self.tcp_socket_connections = int(socket_clients)
            # init request core handler
            self.tcp_socket_handler = WebSocketHandler(self)
            self.tcp_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind(self.tcp_socket_address)
            WebSocket.__instance = self
            print("Socket listener started on " + str(socket_host) + ":"
                  + str(socket_port) + " for " + str(socket_clients) + " listeners")
            # starting listener thread
            threading.Thread(target=self.startup_listener).start()

    def startup_listener(self):
        self.tcp_socket.listen(self.tcp_socket_connections)
        while True:
            self.client, self.address = self.tcp_socket.accept()
            # time for disconnect client if none actions
            self.client.settimeout(60)
            threading.Thread(target=self.listen_to_client,
                             args=(self.client, self.address)).start()

# ---------------------------------
# from socket to client methods
# ---------------------------------
    # method calls every change of global manager props
    def update_node_status(self, manager: object):
        try:
            response = PynodeStatus()
            response.define_object(state=manager.state,
                                   ethereum_host=manager.eth_host,
                                   ipfs_host=manager.ipfs_host+":"+manager.ipfs_port,
                                   pandora_address=manager.eth_pandora,
                                   worker_address=manager.eth_worker,
                                   worker_state=manager.worker_contract_state,
                                   job_address=manager.job_contract_address,
                                   job_status=manager.job_contract_state,
                                   kernel_address=manager.job_kernel_ipfs_address,
                                   dataset_address=manager.job_dataset_ipfs_address,
                                   job_result_address=manager.job_result_ipfs_address)
            if self.client is not None:
                self.client.send(str.encode(ClassApiSerializer().serialize(response)))
        except Exception as ex:
            print(ex)
            return False

    # method calls every time when new log record is append
    def update_log_record(self, record: LogRecord):
        try:
            response = PynodeLogRecord()
            response.define_object(process_name=record.processName,
                                   level_name=record.levelname,
                                   file_name=record.filename,
                                   module=record.module,
                                   message=record.getMessage())
            if self.client is not None:
                self.client.send(str.encode(ClassApiSerializer().serialize(response)))
        except Exception as ex:
            print(ex)
            return False

# ---------------------------------
# from client to socket methods
# ---------------------------------
    # listener for getting request from customer
    # in current realisation {"method":"__name__"} available
    # startup, get_settings, get_status (implemented on handler in WebSocketHandler class)
    def listen_to_client(self, client, address):
        while True:
            try:
                data = client.recv(1024)
                if data:
                    result = self.tcp_socket_handler.handle_request(bytes.decode(data))
                    response = str.encode(ClassApiSerializer().serialize(result))
                    client.send(response)
                else:
                    print('Client disconnected')
            except Exception as ex:
                print(ex)
                return False


