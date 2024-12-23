import socket
import threading
from common.config import HOST, PORT
from common.protocol import Protocol


class ClientManager:
    def __init__(self, logic):
        self.logic = logic
        self.clients = []

    def start_listening(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Сервер запущен на {HOST}:{PORT}")

        threading.Thread(target=self.update_game_state, daemon=True).start()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Клиент подключился: {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        """Обрабатывает команды клиента."""
        try:
            while True:
                header = client_socket.recv(4)
                if not header:
                    break
                length = int.from_bytes(header, "big")
                data = client_socket.recv(length)
                decoded_message = Protocol.decode_message(header + data)

                if decoded_message["type"] == "gun_command":
                    command = decoded_message["payload"]["command"]  # Извлекаем команду из декодированного сообщения
                    self.logic.update_gun(command)
                if decoded_message["type"] == "fire":
                    self.logic.fire_bomb()
                elif decoded_message["type"] == "reset_game":
                    print("Команда сброса игры получена.")
                    self.logic.reset_game()    

        except ConnectionResetError:
            self.clients.remove(client_socket)
            client_socket.close()

    def update_game_state(self):
     while True:
        self.logic.generate_ships()
        self.logic.update_bombs()
        self.logic.check_collisions()
        state_data = Protocol.encode_game_state(self.logic.get_state())

        for client in list(self.clients):
            try:
                client.sendall(state_data)
            except (BrokenPipeError, OSError):
                print("Соединение с клиентом потеряно.")
                self.clients.remove(client)
