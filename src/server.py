import socket
import threading
import time
from session import Session
from client import Client



REBROADCAST_TIMEOUT = 1

BROADCAST_DST_PORT = 13117
SERVER_PORT = 33333
SERVER_ADDR = socket.gethostbyname(socket.gethostname())

clients: list = []
accept_thread = None


def send_broadcast(udp_socket):
    pass


# accept client to the session if available, and wait to start the session
def accept_client(connection_socket, address):
    client_name = connection_socket.recv(1024)
    if len(clients) < 2:
        clients.append(Client(socket=connection_socket, address=address, name=client_name))


def open_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_ADDR, SERVER_PORT))
    server_socket.listen(1)
    print(f'Server started, listening on IP address {SERVER_ADDR}')
    return server_socket


def listen_for_clients(server_socket):

    while not len(clients) < 2:
        conn, address = server_socket.accept()
        accept_client(conn, address)


def send_to_client(client: Client, message: str) -> None:
    conn = client.socket
    conn.send(message)


def start() -> None:
    server_socket = open_tcp_server()
    while True:
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.bind((SERVER_ADDR, BROADCAST_DST_PORT))
        threading.Thread(target=listen_for_clients, args=[server_socket]).start()
        while not len(clients) != 2:
            send_broadcast(broadcast_socket)
            time.sleep(REBROADCAST_TIMEOUT)
        broadcast_socket.close()
        session = Session(send_handler=send_to_client)
        session.add_players(clients)

        session.begin_game()







