import random
import select
import socket
import sys

TIMEOUT = 10

BROADCAST_IP = "127.0.0.255"
SERVER_IP = "localhost"  # Dedicated server IP address - student90
UDP_PORT = 13117  # Dedicated broadcast offer port
TCP_PORT = -1
PORT = random.randint(1024, 65535)  # The port from which the client will send out messages
HOST = socket.gethostbyname(socket.gethostname())
c_socket = None
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'  # All broadcast offer messages MUST begin with this prefix
MESSAGE_TYPE = b'\x02'  # Specifies broadcast offer, no other message types are supported
CLIENT_NAME = b"Timeout tERRORs\n"
FORMAT = "utf-8"  # Decode and encode format for incoming and outgoing messages


# checks if the offer is a valid offer
def handle_offer(offer: bytes):
    global TCP_PORT
    if not offer[0:4].__eq__(MAGIC_COOKIE):
        print("invalid offer, no magic cookie")
        return False
    if not offer[4].__eq__(MESSAGE_TYPE):
        print("invalid offer, no message type")
        return False
    TCP_PORT = int.from_bytes(offer[5:7], "little")
    if TCP_PORT < 0:
        print("invalid offer, not a good port")
        return False
    return True


# function that handles the game logic and ends it gracefully after the game is over
def start_game(sock):
    terminate_game = False
    while not terminate_game:
        reads, _, _ = select.select([sock, sys.stdin], [], [], TIMEOUT)

        if sock in reads:  # received an answer from server i.e. the game is over, print message, close socket
            message = sock.recv(1024)
            print(message.decode(FORMAT))
            sock.close()
            terminate_game = True
        elif sys.stdin in reads:
            answer = sys.stdin.readline(1)
            sock.send(answer.encode())


def main():
    global c_socket
    print(f'Client started, listening on IP address {HOST}:{UDP_PORT}')
    while True:
        # listen to UDP offers
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((BROADCAST_IP, UDP_PORT))
        print("waiting for an offer")
        offer, address = sock.recvfrom(1024)
        print(f"incoming offer: {offer}")
        sock.close()
        # try to  connect to server.
        result = handle_offer(offer)
        # if we got false then the client continues to another offer to look for
        if not result:
            continue
        # requesting a socket for tcp connection and setting it to false
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:  # try to connect to server. will get excepted if server refused to establish connection
            c_socket.connect((SERVER_IP, TCP_PORT))
            # sends the rever the client name
            c_socket.send(CLIENT_NAME)
        except OSError:  # handling the exception for not connecting to server
            print("connection failed, server refused to accept more clients")
            c_socket.close()
        c_socket.recv(1024)  # Wait until receiving welcome
        c_socket.setblocking(False)
        start_game(c_socket)


# configure to a different server address to try to connect to other servers
def configure_game(server_addr=SERVER_IP):
    global SERVER_IP
    SERVER_IP = server_addr


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(sys.argv[1])
        configure_game(sys.argv[1])
    try:
        main()
    except KeyboardInterrupt:
        if c_socket is not None:
            c_socket.close()
