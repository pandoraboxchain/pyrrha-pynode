import sys
from socket import *


def send(*args):
    print("send data")
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    host = 'localhost'
    port = 9090
    address = (host, port)
    tcp_socket.connect(address)

    data = """{"method":"status"}"""
    data = str.encode(data)
    tcp_socket.send(data)
    data = tcp_socket.recv(1024)
    print(data)


if __name__ == "__main__":
    send(sys.argv)


