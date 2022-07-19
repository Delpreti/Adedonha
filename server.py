#!/usr/bin/env python3

import rpyc, argparse, random, string
from rpyc.utils.server import ThreadedServer
from threading import Thread, Timer

CATEGORIES = sorted([
    "Animal",
    "Nome de pessoa",
    # "Fruta",
    # "MSÉ",
    # "Cor",
    # "Marca",
    # "CEP",
    # "Filme/Série",
    # "Personagem",
    # "Parte do corpo humano",
])

class ServerService(rpyc.Service):
    def __init__(self):
        self.clients = []
        self.admin = None
        self.letters = list(string.ascii_uppercase)
        self.answers = {}
        self.voting = {}

        self.exposed_ongoing = False
        self.exposed_paused = True
        self.exposed_usernames = []
        self.exposed_categories = CATEGORIES

    def on_connect(self, conn):
        if self.exposed_ongoing:
            conn.close()

        username = conn.root.username
        if any(x == username for x in self.exposed_usernames):
            conn.close()

        self.announce(f"{username} entrou no jogo.")

        self.clients.append(conn)
        self.exposed_usernames.append(username)

        if self.admin is None:
            self.admin = username
            conn.root.set_admin()

    def on_disconnect(self, conn):
        pass

    def announce(self, message):
        for client in self.clients:
            client.root.print("\r" + message + 50 * " " + "\n> ")

    def start_round(self):
        letter = random.choice(self.letters)
        self.letters.remove(letter)

        for client in self.clients:
            client.root.set_letter(letter)

        self.exposed_paused = False
        self.announce(f"A letra sorteada é {letter}.")

    def exposed_start_game(self):
        if self.exposed_ongoing:
            return
        self.exposed_ongoing = True
        self.announce(f"{self.admin} iniciou o jogo.")
        self.start_round()

    def exposed_stop(self, username):
        self.exposed_paused = True
        self.announce(f"===== {username} - STOP! =====")
        self.vote_round(1)

    def exposed_vote(self, answer):
        usernames = list(self.answers.keys())
        username = usernames[answer - 1]
        self.voting[username] = self.voting.get(username, 0) + 1

        # if sum(x for x in self.voting.values()) == len(self.clients):
        #     self.start_round()

    def vote_round(self, round_num):
        self.answers = {}
        self.voting = {}

        self.announce(f"Categoria: {CATEGORIES[round_num - 1]}")
        self.answers = {x.root.username: x.root.answers[round_num - 1] for x in self.clients if x.root.answers[round_num - 1] is not None}
        for j, answer in enumerate(self.answers.values(), start=1):
            self.announce(f"{j} - {answer}")

        if round_num <= len(CATEGORIES):
            timer = Timer(10, self.end_vote_round, args=(round_num,))
            timer.start()

    def end_vote_round(self, round_num):
        for client in self.clients:
            if client.root.username not in self.voting:
                client.root.add_score()

        if round_num < len(CATEGORIES):
            self.vote_round(round_num + 1)
        else:
            for client in self.clients:
                self.announce(f"{client.root.username} - {client.root.score}")
            self.announce("cabou")


def start_server(port):
    global service
    service = ServerService()
    server = ThreadedServer(service, port=port)
    server.start()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, dest="port", required=True)
    args = parser.parse_args()

    server_thread = Thread(target=start_server, args=(args.port,))
    server_thread.start()

    while True:
        text = input("> ")

if __name__ == "__main__":
    main()
