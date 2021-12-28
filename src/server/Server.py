import random
import socket
import threading
import time

from Session import Session
from Player import Player

REBROADCAST_TIMEOUT = 1  # Broadcast announcement timeout after which another broadcast is sent (1 second)

SERVER_IP = "127.0.0.1"  # socket.gethostbyname(socket.gethostname())  # Acquire local host IP address

BROADCAST_DST_PORT = 13117  # Fixed port number, as defined in the packet formats
BROADCAST_SRC_PORT = random.randint(1024, 65535)  # The port from which to send out offer announcements

# The port from which the server will listen for incoming client connections
SERVER_PORT = random.choice([i for i in range(1024, 65535) if i not in [BROADCAST_SRC_PORT]])
SERVER_PORT_LENGTH = 2  # Port is 2 bytes (16 bits) long

SERVER_ADDR = (SERVER_IP, SERVER_PORT)
BROADCAST_SERVER_ADDR = (SERVER_IP, BROADCAST_SRC_PORT)
BROADCAST_IP = "127.0.0.255"
BROADCAST_DST_ADDR = (BROADCAST_IP, BROADCAST_DST_PORT)

MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE = b'\x02'  # Specifies broadcast offer, no other message types are supported
OFFER_END_INDEX = 8  # UDP broadcast offer messages are of fixed length 7

MAX_CLIENTS = 2  # Amount of clients required to initiate a game session
ANSWER_LENGTH = 2  # Expected length of answer messages

clients: list = []
accept_thread = None


def send_broadcast(udp_socket):
    announcement_message = MAGIC_COOKIE + MESSAGE_TYPE + SERVER_PORT.to_bytes(SERVER_PORT_LENGTH, "little")
    print(f"broadcasting offer - {announcement_message} to: {BROADCAST_DST_ADDR} - debug message")  # TODO - debug message
    udp_socket.sendto(announcement_message[:OFFER_END_INDEX], BROADCAST_DST_ADDR)


# accept client to the session if available, and wait to start the session
def accept_client(connection_socket, address):
    team_name = connection_socket.recv(1024)  # First message from client is their team name
    team_name = team_name.decode()
    connection_socket.setblocking(False)
    if len(clients) < MAX_CLIENTS:
        print(f"accepted client: {len(clients) + 1} - debug message")  # TODO - debug message
        clients.append(Player(socket=connection_socket, address=address, name=team_name))


# Initialize a TCP socket and begin listening for incoming connections
def open_tcp_server():
    # Create a socket instance whose address-family is AF_INET (IPv4)
    # and socket kind is SOCK_STREAM (connection-oriented TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDR)
    # Queue up as many as 'MAX_CLIENTS' connect requests before refusing outside connections
    server_socket.listen(MAX_CLIENTS)
    print(f'Server started, listening on IP address {SERVER_IP}:{SERVER_PORT}')
    return server_socket


def listen_for_clients(server_socket):
    while len(clients) < MAX_CLIENTS:
        conn, address = server_socket.accept()
        accept_client(conn, address)


def send_to_client(client: Player, message: str) -> None:
    conn = client.socket
    conn.send(message.encode())


def receive_from_client(conn):
    message = conn.recv(ANSWER_LENGTH).decode()  # TODO - switch to 'getch'?
    return message


def start() -> None:
    global accept_thread
    server_socket = open_tcp_server()
    while True:
        # Create a socket instance whose address-family is AF_INET (IPv4)
        # and socket kind is SOCK_DGRAM (connectionless UDP)
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.bind(BROADCAST_SERVER_ADDR)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Start a new thread to listen to client connections
        accept_thread = threading.Thread(target=listen_for_clients, args=[server_socket], daemon=True)
        accept_thread.start()
        # Meanwhile, send offer announcements
        while len(clients) < MAX_CLIENTS:
            send_broadcast(broadcast_socket)
            time.sleep(REBROADCAST_TIMEOUT)
        broadcast_socket.close()
        # All clients have connected, initialize game session
        session = Session(send_handler=send_to_client, receive_handler=receive_from_client, players=clients)
        session.begin_game()
        # Disconnect clients and clear the list
        for client in clients:
            client.socket.close()
        clients.clear()


if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        print("server stopped...")
