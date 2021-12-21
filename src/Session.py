import time

from Client import Client


class Session:
    GAME_BEGINS_DELAY = 10

    def __init__(self, send_handler):
        self.p1: Client = None
        self.p2: Client = None
        self.srv_handler = send_handler


    def receive_answers(self, ans):
        pass

    def send_result(self):
        pass

    def send_welcome_message(self):
        message = f'Welcome to Quick-Math!\nPlayer 1: {self.p1.name}.\nPlayer 2: {self.p2.name}\n'
        self.srv_handler(self.p1, message)
        self.srv_handler(self.p2, message)



    def add_players(self, player):
        self.p1 = player[0]
        self.p2 = player[1]

    def begin_game(self):
        self.send_welcome_message()
        time.sleep(self.GAME_BEGINS_DELAY)
