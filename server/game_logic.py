from common.gun import Gun
import random
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT, SHIP_Y_RANGE, SHIP_SPEED_RANGE


class GameLogic:
    def __init__(self):
        self.ships = []
        self.ship_id_counter = 1
        self.gun = Gun(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 70)

    def generate_ships(self):
        if len(self.ships) < 2 and random.random() < 0.02:
            self.ships.append({
                "id": self.ship_id_counter,
                "x": -50,
                "y": random.randint(*SHIP_Y_RANGE),
                "speed": random.uniform(*SHIP_SPEED_RANGE),
            })
            self.ship_id_counter += 1

        for ship in self.ships:
            ship["x"] += ship["speed"] * 0.005

        self.ships = [ship for ship in self.ships if ship["x"] < WINDOW_WIDTH]

    def update_gun(self, command):
        """Обновляет угол поворота пушки на основе команды."""
        if command == "move_left":
            self.gun.rotate("left")
        elif command == "move_right":
            self.gun.rotate("right")

    def get_state(self):
        return {
            "ships": self.ships,
            "gun": {
                "x": self.gun.x,
                "y": self.gun.y,
                "angle": self.gun.angle
            }
        }