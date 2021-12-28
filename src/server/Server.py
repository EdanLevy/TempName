import random
import socket
import threading
import time
from Session import Session
from Player import Player

REBROADCAST_TIMEOUT = 1  # Broadcast announcement timeout after which another broadcast is sent (1 second)

SERVER_IP = socket.gethostbyname(socket.gethostname())  # Acquire local host IP address

MAGIC_COOKIE = "0xabcddcba"  # All broadcast offer messages MUST begin with this prefix
MESSAGE_TYPE = "0x2"  # Specifies broadcast offer, no other message types are supported
BROADCAST_DST_PORT = 13117  # Fixed port number, as defined in the packet formats
BROADCAST_SRC_PORT = random.randint(1024, 65535)  # The port from which to send out offer announcements

# The port from which the server will listen for incoming client connections
SERVER_PORT = random.choice([i for i in range(1024, 65535) if i not in [BROADCAST_SRC_PORT]])

SERVER_ADDR = (SERVER_IP, SERVER_PORT)
BROADCAST_SERVER_ADDR = (SERVER_IP, BROADCAST_SRC_PORT)

FORMAT = 'utf-8'  # Decode and encode format for incoming and outgoing messages
MAX_CLIENTS = 2  # Amount of clients required to initiate a game session
ANSWER_LENGTH = 2  # Expected length of answer messages

clients: list = []
accept_thread = None


def send_broadcast(udp_socket):
    announcement_message = MAGIC_COOKIE + MESSAGE_TYPE + str(SERVER_PORT)
    udp_socket.send(announcement_message.encode(FORMAT))


# accept client to the session if available, and wait to start the session
def accept_client(connection_socket, address):
    client_name = connection_socket.recv(1024)  # First message from client is expected to be their name
    client_name = client_name.decode(FORMAT).split('\n')[0]
    if len(clients) < MAX_CLIENTS:
        clients.append(Player(socket=connection_socket, address=address, name=client_name))


# Initialize a TCP socket and begin listening for incoming connections
def open_tcp_server():
    # Create a socket instance whose address-family is AF_INET (IPv4)
    # and socket kind is SOCK_STREAM (connection-oriented TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDR)
    # Queue up as many as 'MAX_CLIENTS' connect requests before refusing outside connections
    server_socket.listen(MAX_CLIENTS)
    print(f'Server started, listening on IP address {SERVER_IP}')
    return server_socket


def listen_for_clients(server_socket):
    while len(clients) < MAX_CLIENTS:
        conn, address = server_socket.accept()
        accept_client(conn, address)


def send_to_client(client: Player, message: str) -> None:
    conn = client.socket
    conn.send(message.encode(FORMAT))


def receive_from_client(conn):
    message = conn.recv(ANSWER_LENGTH).decode(FORMAT)  # TODO - switch to 'getch'?
    return message


def start() -> None:
    server_socket = open_tcp_server()
    while True:
        # Create a socket instance whose address-family is AF_INET (IPv4)
        # and socket kind is SOCK_DGRAM (connectionless UDP)
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.bind(BROADCAST_SERVER_ADDR)
        # Start a new thread to listen to client connections
        threading.Thread(target=listen_for_clients, args=[server_socket]).start()
        # Meanwhile, send offer announcements
        while len(clients) < MAX_CLIENTS:
            send_broadcast(broadcast_socket)
            time.sleep(REBROADCAST_TIMEOUT)
        broadcast_socket.close()
        # All clients have connected, initialize game session
        session = Session(send_handler=send_to_client, players=clients)
        session.begin_game()
        # Disconnect clients and clear the list
        for client in clients:
            client.socket.close()
        clients.clear()


if __name__ == "__main__":
    start()
