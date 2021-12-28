import random
import select
import socket
import sys

TIMEOUT = 10

BROADCAST_IP = "127.0.0.255"
UDP_PORT = 13117  # Dedicated broadcast offer port

SERVER_IP = "localhost"  # Dedicated server IP address - student90
TCP_PORT = -1
MIN_VALID_PORT = 0

PORT = random.randint(1024, 65535)  # The port from which the client will send out messages
HOST = socket.gethostbyname(socket.gethostname())

IP_INDEX = 0  # In an address tuple, the IP is the first element

MAGIC_COOKIE = b'\xab\xcd\xdc\xba'  # All broadcast offer messages MUST begin with this prefix
MAGIC_COOKIE_START = 0  # The index in the offer announcement where the magic cookie starts
MAGIC_COOKIE_END = 4  # The index in the offer announcement where the magic cookie ends

MESSAGE_TYPE = b'\x02'  # Specifies broadcast offer, no other message types are supported
MESSAGE_TYPE_INDEX = 4  # The index in the offer announcement where the message type is

SERVER_PORT_START = 5  # The index in the offer announcement where the server port starts
SERVER_PORT_END = 7  # The index in the offer announcement where the server port ends

TEAM_NAME = b"Timeout tERRORs\n"

c_socket = None


# checks if the offer is a valid offer
def handle_offer(offer: bytes):
    global TCP_PORT
    if not offer[MAGIC_COOKIE_START:MAGIC_COOKIE_END].__eq__(MAGIC_COOKIE):
        print("Offer doesn't start with magic cookie. Rejecting offer.")
        return False
    if not offer[MESSAGE_TYPE_INDEX].__eq__(MESSAGE_TYPE):
        print("Message type not support. Rejecting offer.")
        return False
    TCP_PORT = int.from_bytes(offer[SERVER_PORT_START:SERVER_PORT_END], "little")
    if TCP_PORT < MIN_VALID_PORT:
        print("Invalid port. Rejecting offer.")
        return False
    return True


# function that handles the game logic and ends it gracefully after the game is over
def start_game(sock):
    terminate_game = False
    while not terminate_game:
        reads, _, _ = select.select([sock, sys.stdin], [], [], TIMEOUT)

        if sock in reads:  # received an answer from server i.e. the game is over, print message, close socket
            message = sock.recv(1024)
            print(message.decode())
            sock.close()
            terminate_game = True
        elif sys.stdin in reads:
            answer = sys.stdin.readline(1)
            sock.send(answer.encode())


def main():
    global c_socket
    print("Client started, listening for offer requests...")
    # print(f'Listening on address {HOST} : {UDP_PORT} - debug message')  # TODO - debug message
    while True:
        # listen to UDP offers
        offer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        offer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        offer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        offer_socket.bind((BROADCAST_IP, UDP_PORT))
        # print("waiting for an offer - debug message")  # TODO - debug message
        offer, server_address = offer_socket.recvfrom(1024)
        # print(f"incoming offer: {offer} - debug message")  # TODO - debug message
        offer_socket.close()
        # try to connect to server
        result = handle_offer(offer)
        # if the offer is invalid then the client continues to look for other offers
        if not result:
            continue
        print(f"Received offer from {server_address[IP_INDEX]}, attempting to connect...")
        # requesting a socket for tcp connection and setting it to false
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:  # try to connect to server. will get excepted if server refused to establish connection
            c_socket.connect((SERVER_IP, TCP_PORT))
            # sends the server the client name
            c_socket.send(TEAM_NAME)
        except OSError:  # handling the exception for not connecting to server
            # print("connection failed, server refused to accept more clients - debug message")  # TODO - debug message
            c_socket.close()
            print("Server disconnected, listening for offer requests...")
        print(c_socket.recv(1024).decode())  # Wait until receiving welcome message and math problem and print it
        c_socket.setblocking(False)
        start_game(c_socket)
        print("Server disconnected, listening for offer requests...")


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
