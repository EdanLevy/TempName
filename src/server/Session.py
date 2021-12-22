import threading
import time
import random

from Player import Player


class Session:
    GAME_BEGINS_DELAY = 10
    GAME_TIMEOUT = 10
    math_questions: dict = {"2+2": 4}  # TODO

    def __init__(self, send_handler, receive_handler, players):
        self.p1 = players[0]
        self.p2 = players[1]
        self.receive_handler = receive_handler
        self.send_handler = send_handler
        self.results = {self.p1: [], self.p2: []}  # Initialize dictionary that contains results regarding each player
        self.the_question = random.choice(list(self.math_questions.keys()))
        self.the_answer = self.math_questions.get(self.the_question)
        self.the_winner = None
        self.threads = []
        self.received_answer = False

    def handle_timeout(self, callback):
        time.sleep(self.GAME_TIMEOUT)
        callback(None)

    def receive_answers(self):
        self.threads += threading.Thread(target=self.receive_handler, args=[self.p1, self.results, self.notify_session])
        self.threads += threading.Thread(target=self.receive_handler, args=[self.p2, self.results, self.notify_session])
        for t in self.threads:
            t.start()
        threading.Thread(target=self.handle_timeout, args=[self.notify_session])
        # TODO - handle threads that did not terminate
        for t in self.threads:
            t.join()

    def notify_session(self, player):
        with threading.Lock():
            if not self.received_answer:
                self.received_answer = True
                # TODO - handle other thread that did not necessarily terminate
                self.check_send_result(player)

    def send_result(self):
        pass

    def send_welcome_message(self):
        message = f'Welcome to Quick Maths.\nPlayer 1: {self.p1.name}.\nPlayer 2: {self.p2.name}\n==\n'
        self.send_message_to_players(message)

    def send_math_problem(self):
        pre_message = "Please answer the following question as fast as you can:\n"
        question = "How much is " + self.the_question + "?\n"
        message = pre_message + question
        self.send_message_to_players(message)

    def finish_game(self):
        message = "Game over, sending out offer requests...\n"
        self.send_message_to_players(message)

    def begin_game(self):
        time.sleep(self.GAME_BEGINS_DELAY)
        self.send_welcome_message()
        self.send_math_problem()
        self.receive_answers()
        self.send_result()
        self.finish_game()
