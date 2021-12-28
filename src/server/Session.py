import select
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

    def receive_answers(self):
        read_ready, _, _ = select.select([self.p1.socket, self.p2.socket], [], [], self.GAME_TIMEOUT)
        player = None
        for sock in read_ready:
            player = self.p1 if sock is self.p1.socket else self.p2
            answer = self.receive_handler(player)
            self.results[player][0] = answer
            break  # Once 1 player has sent an answer, the game is decided
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
