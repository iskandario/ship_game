import json
import struct


class Protocol:
    HEADER_FORMAT = "!I"  # Формат заголовка: длина сообщения (4 байта)

    @staticmethod
    def encode_message(message_type, payload):
        """
        Кодирует сообщение: сериализация в JSON, преобразование в бинарный формат.
        """
        dto = {
            "type": message_type,
            "payload": payload,
        }
        json_data = json.dumps(dto).encode("utf-8")  # Преобразуем JSON в байты
        length = len(json_data)

        # Формируем заголовок и сообщение
        header = struct.pack(Protocol.HEADER_FORMAT, length)
        return header + json_data

    @staticmethod
    def decode_message(data):
        """
        Декодирует бинарное сообщение обратно в JSON.
        """
        header_size = struct.calcsize(Protocol.HEADER_FORMAT)
        message_length = struct.unpack(Protocol.HEADER_FORMAT, data[:header_size])[0]
        json_data = data[header_size:header_size + message_length]
        return json.loads(json_data.decode("utf-8"))

    # Методы для работы с пушкой
    @staticmethod
    def encode_gun_command(command):
        """
        Кодирует команду управления пушкой (от клиента).
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
    def encode_bomb_command():
        return Protocol.encode_message("fire", {})