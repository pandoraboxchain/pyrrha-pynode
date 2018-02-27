import socket
import threading
import webapi

from logging import LogRecord
from socket import *
from webapi.web_socket_handler import WebSocketHandler


class WebSocket(threading.Thread):

    __instance = None

    tcp_socket = None
    tcp_socket_address = None
    tcp_socket_handler = None
    tcp_socket_connections = None

    client = None
    address = None

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
            self.tcp_socket_handler = webapi.web_socket_handler.WebSocketHandler(self)
            self.tcp_socket = socket(AF_INET, SOCK_STREAM)
            self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.tcp_socket.bind(self.tcp_socket_address)
            WebSocket.__instance = self
            print("Socket listener started on " + str(socket_host) + ":"
                  + str(socket_port) + " for " + str(socket_clients) + " listeners")
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
    def update_client_status(self, data):
        try:
            self.client.send(str.encode(data))
        except Exception as ex:
            print(ex)
            return False

    def update_log_record(self, record: LogRecord):
        try:
            self.client.send(str.encode(record.msg))
        except Exception as ex:
            print(ex)
            return False

# ---------------------------------
# from client to socket methods
# ---------------------------------
    def listen_to_client(self, client, address):
        while True:
            try:
                data = client.recv(1024)
                if data:
                    response = str.encode(self.tcp_socket_handler.handle_request(bytes.decode(data)))
                    client.send(response)
                else:
                    print('Client disconnected')
            except Exception as ex:
                client.close()
                return False


