import random
import select
import socket
import sys
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


# checks if the offer is a valid offer
def handle_offer(offer: bytes):
    global TCP_PORT
    magic_exist = offer.startswith(MAGIC_COOKIE, 0, 4)
    if not magic_exist:
        print("invalid offer, no magic cookie")
        return False
    if offer[4] is not MESSAGE_TYPE:
        print("invalid offer, no message type")
        return False
    TCP_PORT = int(offer[5:])
    if TCP_PORT < 0:
        print("invalid offer, not a good port")
        return False
    return True


# function that handles the game logic and ends it gracefully after the game is over
def start_game(sock):
    terminate_game = False
    while not terminate_game:
        reads, _, _ = select.select([sock, sys.stdin], [], [], 10)

        if sock in reads:  # received an answer from server i.e. the game is over, print message, close socket
            message = sock.recv(1024)
            print(message.decode("UTF-8"))
            sock.close()
            terminate_game = True
        elif sys.stdin in reads:
            answer = sys.stdin.readline(1)
            sock.send(answer.encode())


def main():
    global c_socket
    print(f'Client started, listening on IP address {HOST}')
    while True:
        # listen to UDP offers
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SERVER_IP, UDP_PORT))
        offer, address = sock.recvfrom(8)
        # try to  connect to server.
        result = handle_offer(offer)
        # if we got false then the client continues to another offer to look for
        if not result:
            continue
        # requesting a socket for tcp connection and setting it to false
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_socket.setblocking(False)
        try:  # try to connect to server. will get excepted if server refused to establish connection
            c_socket.connect((SERVER_IP, TCP_PORT))
            # sends the rever the client name
            c_socket.send(CLIENT_NAME)
        except Union[TimeoutError, InterruptedError]:  # handling the exception for not connecting to server
            print("connection failed, server refused to accept more clients")
            c_socket.close()

        start_game(c_socket)

# configure to a different server address to try to connect to other servers
def configure_game(server_addr=SERVER_IP):
    global SERVER_IP
    SERVER_IP = server_addr


if __name__ == "__main__":
    configure_game(sys.argv[1])
    main()
