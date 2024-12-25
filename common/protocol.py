import socket
import json
import struct

class Protocol:
    HEADER_FORMAT = "!I"  # Формат заголовка: длина сообщения (4 байта)
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    @staticmethod
    def encode_message(message_type, payload):
        """
        Кодирует сообщение и отправляет его через указанный сокет.
        """
        # Создаем сообщение DTO
        dto = {
            "type": message_type,
            "payload": payload
        }
        # Преобразуем в JSON и затем в байты
        json_data = json.dumps(dto).encode("utf-8")
        # Определяем длину сообщения
        length = len(json_data)
        # Формируем заголовок
        header = struct.pack(Protocol.HEADER_FORMAT, length)
        return header + json_data

    @staticmethod
    def decode_message(data):
        """
        Получает и декодирует сообщение из указанных данных.
        """
        # Определяем длину сообщения
        header_size = struct.calcsize(Protocol.HEADER_FORMAT)
        message_length = struct.unpack(Protocol.HEADER_FORMAT, data[:header_size])[0]
        json_data = data[header_size:header_size + message_length]
        # Декодируем JSON обратно в объект
        return json.loads(json_data.decode("utf-8"))

    @staticmethod
    def encode_gun_command(command):
        """
        Кодирует команду управления пушкой.
        """
        return Protocol.encode_message("gun_command", {"command": command})

    @staticmethod
    def decode_gun_command(data):
        """
        Декодирует команду управления пушкой.
        """
        message = Protocol.decode_message(data)
        if message["type"] != "gun_command":
            raise ValueError(f"Неподдерживаемый тип сообщения: {message['type']}")
        return message["payload"]["command"]

    @staticmethod
    def encode_game_state(state):
        """
        Кодирует состояние игры (корабли и пушка).
        """
        return Protocol.encode_message("state_update", state)

    @staticmethod
    def decode_game_state(data):
        """
        Декодирует состояние игры (корабли и пушка).
        """
        message = Protocol.decode_message(data)
        if message["type"] != "state_update":
            raise ValueError(f"Неподдерживаемый тип сообщения: {message['type']}")
        return message["payload"]

    @staticmethod
    def encode_reset_command():
        """
        Кодирует команду сброса состояния игры.
        """
        return Protocol.encode_message("reset_game", {})

    @staticmethod
    def encode_bomb_command():
        """
        Кодирует команду выстрела.
        """
        return Protocol.encode_message("fire", {})
