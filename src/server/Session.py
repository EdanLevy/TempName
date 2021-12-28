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
            answer = self.receive_handler(sock)
            self.results.get(player)[0] = answer
            break  # Once 1 player has sent an answer, the game is decided
        self.check_send_result(player)

    def check_send_result(self, p: Player):
        if p is None:
            self.the_winner = None
        else:
            actual = int(self.results[p][0])

            if actual == self.the_answer:
                self.the_winner = p.name
            else:
                self.the_winner = self.p2.name if p == self.p1 else self.p1.name

    def send_message_to_players(self, message: str):
        self.send_handler(self.p1, message)
        self.send_handler(self.p2, message)

    def send_result(self):
        message = f"Game over!\nThe correct answer was  {self.the_answer}!\n\n  " \
                  f"Congratulations to the winner: {self.the_winner}\n"
        self.send_message_to_players(message)

    def send_game_messages(self):
        welcome_message = f'Welcome to Quick Maths.\nPlayer 1: {self.p1.name}.\nPlayer 2: {self.p2.name}\n==\n' \
                          f'Please answer the following question as fast as you can:\n'
        question = "How much is " + self.the_question + "?\n"
        message = welcome_message + question
        self.send_message_to_players(message)

    def finish_game(self):
        message = "Game over, sending out offer requests...\n"
        self.send_message_to_players(message)

    def begin_game(self):
        time.sleep(self.GAME_BEGINS_DELAY)
        self.send_game_messages()
        self.receive_answers()
        self.send_result()
        self.finish_game()
