import sys
from socket import *


def send_set_settings() -> str:
    return """{"method": "set_settings","pynode_settings":{"pynode_config_file_path":"test","pynode_launch_mode": "1","ethereum_connection_use": "local","ethereum_connection_host": "localhost","ipfs_connection_use": "infura","ipfs_connection_host": "infura","pandora_contract_address": "0x0","worker_contract_address": "0x0"}}"""


def send_get_settings() -> str:
    return """{"method":"get_settings"}"""


def send_launch_pynode() -> str:
    return """{"method":"startup"}"""


def send(*args):
    print("send data")
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    host = 'localhost'
    port = 9090
    address = (host, port)
    tcp_socket.connect(address)

    data = send_launch_pynode()
    data = str.encode(data)
    tcp_socket.send(data)
    data = tcp_socket.recv(1024)
    while len(data) > 0:
        print("receive :" + str(data))
        data = tcp_socket.recv(1024)


if __name__ == "__main__":
    send(sys.argv)


