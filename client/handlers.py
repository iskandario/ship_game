import socket
import threading
from common.protocol import Protocol
from common.config import HOST, PORT


class ClientHandler:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = {"ships": [], "gun": {"x": 0, "y": 0, "angle": 90}}  # Инициализация состояния

        self.socket.connect((HOST, PORT))
        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def listen_to_server(self):
        while True:
            try:
                header = self.socket.recv(4)  # Получаем длину сообщения
                if not header:
                    break
                length = int.from_bytes(header, "big")
                data = self.socket.recv(length)
                decoded_message = Protocol.decode_message(header + data)
                if decoded_message["type"] == "state_update":
                    self.state = decoded_message["payload"]
            except ConnectionResetError:
                break

    def send_gun_command(self, command):
        message = Protocol.encode_gun_command(command)
        try:
            self.socket.sendall(message)
        except BrokenPipeError:
            print("Соединение с сервером потеряно.")

    def send_fire_command(self):
        """Отправляет команду выстрела на сервер."""
        message = Protocol.encode_message("fire", {})
        try:
            self.socket.sendall(message)
        except BrokenPipeError:
            print("Соединение с сервером потеряно.")

    def get_state(self):
        """Возвращает текущее состояние игры."""
        return self.state