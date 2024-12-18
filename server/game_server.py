from server.game_logic import GameLogic
from server.client_manager import ClientManager


class GameServer:
    def __init__(self):
        self.logic = GameLogic()
        self.client_manager = ClientManager(self.logic)

    def run(self):
        self.client_manager.start_listening()


if __name__ == "__main__":
    server = GameServer()
    server.run()