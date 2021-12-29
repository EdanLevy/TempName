import math
import select
import time
import random

from Player import Player


class Session:
    GAME_BEGINS_DELAY = 10
    GAME_TIMEOUT = 10

    def __init__(self, send_handler, receive_handler, players):
        self.p1 = players[0]
        self.p2 = players[1]
        self.receive_handler = receive_handler
        self.send_handler = send_handler
        self.results = {self.p1: [], self.p2: []}  # Initialize dictionary that contains results regarding each player
        self.the_question = None
        self.the_answer = None
        self.the_winner = None

    def set_up_math_question(self):
        math_questions = {}

        # The sum of 'digit_count' digits
        digit_count = random.randint(2, 9)
        total = 9
        nums = []
        for i in range(digit_count):
            val = random.randint(0, total)
            nums.append(val)
            total -= val
        question = "+".join(map(str, nums))
        answer = sum(nums)
        math_questions[question] = answer

        # Simple 'Ax+B' derivative
        deriv = random.randint(1, 9)
        free = random.randint(0, 9)
        free = f"+{free}" if free != 0 else ""
        question = f'({deriv}x{free})\''
        answer = deriv
        math_questions[question] = answer

        # Factorial of some number between 0 and 3
        fact = random.randint(0, 3)
        question = f"{fact}!"
        answer = math.factorial(fact)
        math_questions[question] = answer

        # Absolute value of a digit
        abs_num = random.randint(-9, 9)
        question = f"|{abs_num}|"
        answer = abs(abs_num)
        math_questions[question] = answer

        # Absolute value of i to the power of anything
        i = random.randint(0, 100)
        question = f"|i^{i}|"
        answer = 1
        math_questions[question] = answer

        # Hitchhiker's Guide to the Galaxy
        dig = random.randint(0, 1)
        if dig == 0:
            question = "the answer to life, the universe, and everything (first digit)"
            answer = 4
        else:
            question = "the answer to life, the universe, and everything (second digit)"
            answer = 2
        math_questions[question] = answer

        self.the_question = random.choice(list(math_questions.keys()))
        self.the_answer = math_questions[self.the_question]

    def send_message_to_players(self, message: str):
        self.send_handler(self.p1, message)
        self.send_handler(self.p2, message)

    def send_game_messages(self):
        welcome_message = f'Welcome to Quick Maths.\nPlayer 1: {self.p1.name}Player 2: {self.p2.name}==\n' \
                          f'Please answer the following question as fast as you can:\n'
        question = f"How much is {self.the_question}?"
        message = welcome_message + question
        self.send_message_to_players(message)

    def receive_answers(self):
        read_ready, _, _ = select.select([self.p1.socket, self.p2.socket], [], [], self.GAME_TIMEOUT)
        player = None
        for sock in read_ready:
            answer = "a"  # default non-numeric value to allow entrance to the while loop
            player = self.p1 if sock is self.p1.socket else self.p2
            while not answer[0].isnumeric():
                answer = self.receive_handler(sock)
            self.results.get(player).append(answer)
            break  # Once 1 player has sent an answer, the game is decided
        self.check_send_result(player)

    def check_send_result(self, p: Player):
        if p is None:
            self.the_winner = None
        else:
            actual = int(self.results.get(p)[0])
            if actual == self.the_answer:
                self.the_winner = p.name
            else:
                self.the_winner = self.p2.name if p == self.p1 else self.p1.name

    def send_result(self):
        message = f"Game over!\nThe correct answer was  {self.the_answer}!\n\n" \
                  f"Congratulations to the winner: {self.the_winner}\n"
        self.send_message_to_players(message)

    def begin_game(self):

        time.sleep(self.GAME_BEGINS_DELAY)
        self.send_game_messages()
        self.receive_answers()
        self.send_result()
