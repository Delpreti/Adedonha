#!/usr/bin/env python3

import rpyc, argparse

class ClientService(rpyc.Service):
    def __init__(self, username):
        self.admin = False
        self.letter = None

        self.exposed_username = username
        self.exposed_answers = None

    def exposed_set_admin(self):
        self.admin = True

    def exposed_set_letter(self, letter):
        self.letter = letter

    def exposed_print(self, msg):
        print(msg, end="", flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", dest="host", required=True)
    parser.add_argument("-p", "--port", type=int, dest="port", required=True)
    parser.add_argument("-u", "--username", dest="username", required=True)
    args = parser.parse_args()

    service = ClientService(args.username)
    conn = rpyc.connect(args.host, args.port, service=service)
    bgsrv = rpyc.BgServingThread(conn)

    service.exposed_answers = [None for _ in range(len(conn.root.categories))]

    while True:
        text = input("> ")
        split = text.split(" ")
        cmd = split[0]
        args = split[1:]

        if cmd == "start":
            if not service.admin:
                print("Você não pode fazer isso.")
                continue
            conn.root.start_game()

        elif cmd == "users":
            print("Lista de usuários no jogo:")
            for username in conn.root.usernames:
                print(username)

        elif cmd == "categories":
            print("Lista de categorias:")
            for (i, category), answer in zip(enumerate(conn.root.categories, start=1), service.exposed_answers):
                print(f"{i} - {category} = {'Vazio' if answer is None else answer}")

        elif cmd == "set":
            if len(args) < 2:
                print("Você precisa especificar o número da categoria e sua resposta.")
                continue

            try:
                category = int(args[0]) - 1
            except ValueError:
                print("O primeiro argumento deve ser o número da categoria.")
                continue

            if not 1 <= category <= len(service.exposed_answers):
                print("Não existe uma categoria com esse número.")
                continue

            answer = " ".join(args[1:])
            service.exposed_answers[category] = answer

        elif cmd == "stop":
            if any(x is None for x in service.exposed_answers):
                print("Você ainda não respondeu todas as categorias.")
                continue

            conn.root.stop(args.username)

        else:
            print("Comando desconhecido.")

if __name__ == "__main__":
    main()
