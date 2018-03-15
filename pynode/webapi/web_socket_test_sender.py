import sys
from socket import socket


# ---------------------------------
# test socket launcher/listener
# ---------------------------------
def send_get_settings() -> str:
    return """{"method":"get_settings"}"""


def send_get_status() -> str:
    return """{"method":"get_status"}"""


def send_launch_pynode() -> str:
    return """{"method":"startup"}"""


def send(*args):
    print("send data")
    tcp_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 9090
    address = (host, port)
    tcp_socket.connect(address)
# change data for send different commands to socket
    data = send_launch_pynode()

    data = str.encode(data)
    tcp_socket.send(data)
    data = tcp_socket.recv(1024)
    while len(data) > 0:
        print("receive :" + str(data))
        data = tcp_socket.recv(1024)


if __name__ == "__main__":
    send(sys.argv)


