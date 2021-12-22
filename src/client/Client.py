import random
import socket
from typing import Union

MAGIC_COOKIE = b"0xabcddcba"  # All broadcast offer messages MUST begin with this prefix
MESSAGE_TYPE = b"0x2"  # Specifies broadcast offer, no other message types are supported

CLIENT_NAME = b"Timeout tErrorS\n"
SERVER_IP = "172.1.0.90"
UDP_PORT = 13117
TCP_PORT = -1
PORT = random.randint(1024, 65535)
HOST = socket.gethostbyname(socket.gethostname())
c_socket = None


def handle_offer(offer: bytes):
    global TCP_PORT
    magic_exist = offer.startswith(MAGIC_COOKIE, 0, 4)
    if not magic_exist:
        print("invalid offer, no magic cookie")
        return False
    if offer[4] is not MESSAGE_TYPE:
        print("invalid offer, no message type")
        return False
    TCP_PORT = int(offer[4:])
    if TCP_PORT < 0:
        print("invalid offer, not a good port")
        return False
    return True


def start_game(sock):
    question = sock.recv(1024).decode("UTF-8").split("\n")[0]
    print(f'{question}\n')
    ans = input()
    if len(ans) > 1:
        print("one digit answer is required")
        return
    sock.send(bytes(ans))
    summery = sock.recv(1024)
    print(str(summery))
    sock.close()
    print("Disconnected from server, listening for offerings...")


def main():
    global c_socket
    print(f'Client started, listening on IP address {HOST}')
    while True:
        # listen to UDP offers
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SERVER_IP, UDP_PORT))
        offer, address = sock.recvfrom(8)
        result = handle_offer(offer)
        if not result:
            continue
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            c_socket.connect((SERVER_IP, TCP_PORT))
            c_socket.send(CLIENT_NAME)
            break
        except Union[TimeoutError, InterruptedError]:
            print("connection failed, server refused to accept more clients")
            c_socket.close()
        start_game(c_socket)


if __name__ == "__main__":
    main()
