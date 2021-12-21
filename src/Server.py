import random
import socket
import threading
import time
from Session import Session
from Client import Client

REBROADCAST_TIMEOUT = 1

SERVER_IP = socket.gethostbyname(socket.gethostname())  # Acquire local host IP address

BROADCAST_DST_PORT = 13117  # Fixed port number, as defined in the packet formats
BROADCAST_SRC_PORT = random.randint(1024, 65535)  # The port from which to send out offer announcements

SERVER_PORT = 33333  # The port from which the server will listen for incoming client connections

SERVER_ADDR = (SERVER_IP, SERVER_PORT)
BROADCAST_SERVER_ADDR = (SERVER_IP, BROADCAST_SRC_PORT)

MAX_CLIENTS = 2  # Amount of clients required to initiate a game session

clients: list = []
accept_thread = None


def send_broadcast(udp_socket):
    # TODO - define and send offer announcements according to 'Packet Formats'
    pass


# accept client to the session if available, and wait to start the session
def accept_client(connection_socket, address):
    client_name = connection_socket.recv(1024)
    if len(clients) < MAX_CLIENTS:
        clients.append(Client(socket=connection_socket, address=address, name=client_name))


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
    while not len(clients) < MAX_CLIENTS:
        conn, address = server_socket.accept()
        accept_client(conn, address)


def send_to_client(client: Client, message: str) -> None:
    conn = client.socket
    conn.send(message)


def start() -> None:
    server_socket = open_tcp_server()
    while True:
        # Create a socket instance whose address-family is AF_INET (IPv4)
        # and socket kind is SOCK_DGRAM (connectionless UDP)
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.bind(BROADCAST_SERVER_ADDR)
        threading.Thread(target=listen_for_clients, args=[server_socket]).start()
        while not len(clients) != MAX_CLIENTS:
            send_broadcast(broadcast_socket)
            time.sleep(REBROADCAST_TIMEOUT)
        broadcast_socket.close()
        session = Session(send_handler=send_to_client)
        session.add_players(clients)

        session.begin_game()
