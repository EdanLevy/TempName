class Session:

    def __init__(self, send_handler):
        self.p1 = None
        self.p2 = None
        self.srv = send_handler

    def send_question(self):
        pass

    def receive_answers(self, ans):
        pass

    def send_result(self):
        pass

    def add_player1(self, player):
        pass


    def add_player2(self, player):
        pass