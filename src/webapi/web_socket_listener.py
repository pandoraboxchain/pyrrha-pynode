import threading

from socket import *

from webapi.web_socket_handler import WebSocketHandler


class WebSocket(threading.Thread):

    tcp_socket_address = None
    tcp_socket = None
    tcp_socket_handler = None

    # base class for init and launch socket thread for monitoring pynode states
    def __init__(self, host: str, port: int):
        self.tcp_socket_address = (host, port)

        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.bind(self.tcp_socket_address)
        self.tcp_socket_handler = WebSocketHandler(0)

    def startup_listener(self):
        self.tcp_socket.listen(1)
        while True:
            client, address = self.tcp_socket.accept()
            client.settimeout(60)
            threading.Thread(target=self.listen_to_client, args=(client, address)).start()

    def shutdown_socket(self):
        self.tcp_socket.close()

    def listen_to_client(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    response = str.encode(self.tcp_socket_handler.handle_request(bytes.decode(data)))
                    client.send(response)
                else:
                    raise error('Client disconnected')
            except Exception as ex:
                client.close()
                return False


