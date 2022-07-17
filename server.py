#!/usr/bin/env python3

import rpyc, argparse, random, string
from rpyc.utils.server import ThreadedServer
from threading import Thread

CATEGORIES = sorted([
    "Animal",
    "Nome de pessoa",
    "Fruta",
    "MSÉ",
])

class ServerService(rpyc.Service):
    def __init__(self):
        self.ongoing = False
        self.clients = []
        self.admin = None

        self.exposed_usernames = []
        self.exposed_categories = CATEGORIES

    def on_connect(self, conn):
        if self.ongoing:
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
        letter = random.choice(string.ascii_uppercase)
        self.announce(f"A letra sorteada é {letter}.")

    def exposed_start_game(self):
        if self.ongoing:
            return
        self.ongoing = True
        self.announce(f"{self.admin} iniciou o jogo.")
        self.start_round()

    def exposed_stop(self, username):
        pass

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
