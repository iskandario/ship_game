from common.gun import Gun
import random
import math
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT, SHIP_Y_RANGE, SHIP_SPEED_RANGE


class GameLogic:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Сбрасывает состояние игры для новой сессии."""
        self.ships = []
        self.bombs = []
        self.ship_id_counter = 1
        self.ships_destroyed = 0
        self.shots_fired = 0  
        self.gun = Gun(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 70)

    def generate_ships(self):
        self.ships = [
            ship for ship in self.ships
            if not ship.get("out_of_bounds") and not ship.get("exploding")
        ]
        if len(self.ships) < 2 and random.random() < 0.02:
            self.ships.append({
                "id": self.ship_id_counter,
                "x": -50,
                "y": random.randint(*SHIP_Y_RANGE),
                "speed": random.uniform(*SHIP_SPEED_RANGE),
                "out_of_bounds": False,
                "exploding": False,
                "explosion_timer": 0,
            })
            self.ship_id_counter += 1
        for ship in self.ships:
            ship["x"] += ship["speed"] * 0.005
            if ship["x"] >= WINDOW_WIDTH:
                ship["out_of_bounds"] = True

    def fire_bomb(self):
        if len(self.bombs) < 10:  # Ограничение на 10 активных снарядов
            tip_x, tip_y = self.gun.get_tip_position()
            self.bombs.append(Bomb(tip_x, tip_y, self.gun.angle))
            self.shots_fired += 1


    def update_gun(self, command):
            """Обновляет угол пушки на основе команды."""
            if command == "move_left":
                self.gun.rotate("left")
            elif command == "move_right":
                self.gun.rotate("right")
                

    def update_bombs(self):
        for bomb in self.bombs:
            bomb.move()
        self.bombs = [bomb for bomb in self.bombs if not bomb.is_out_of_bounds()]

    def check_collisions(self):
        for bomb in list(self.bombs):
            for ship in list(self.ships):
                if ship["x"] < bomb.x < ship["x"] + 50 and ship["y"] < bomb.y < ship["y"] + 40:
                    ship["exploding"] = True
                    ship["explosion_timer"] = 30
                    self.bombs.remove(bomb)
                    self.ships_destroyed += 1
                    break

    def is_game_over(self):
        """Проверяет, завершена ли игра."""
        return self.shots_fired >= 10 and len(self.bombs) == 0  # Все выстрелы сделаны и улетели

    def get_state(self):
        return {
            "ships": self.ships,
            "bombs": [{"x": bomb.x, "y": bomb.y} for bomb in self.bombs],
            "explosions": [{"x": ship["x"], "y": ship["y"]} for ship in self.ships if ship["exploding"]],
            "gun": {
                "x": self.gun.x,
                "y": self.gun.y,
                "angle": self.gun.angle,
            },
            "ships_destroyed": self.ships_destroyed,
        }


class Bomb:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 1  # Скорость бомбы

    def move(self):
        self.x += self.speed/200 * math.cos(math.radians(self.angle))
        self.y -= self.speed/200 * math.sin(math.radians(self.angle))

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT