from common.gun import Gun
import random
import math
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT, SHIP_Y_RANGE, SHIP_SPEED_RANGE


class GameLogic:
    def __init__(self):
        self.ships = []
        self.bombs = []
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

    def fire_bomb(self):
        tip_x, tip_y = self.gun.get_tip_position()  # Конец дула пушки
        self.bombs.append(Bomb(tip_x, tip_y, self.gun.angle))  # Создаем снаряд с правильной позицией


    def update_bombs(self):
        for bomb in self.bombs:
            bomb.move()
        self.bombs = [bomb for bomb in self.bombs if not bomb.is_out_of_bounds()]


    def check_collisions(self):
        for bomb in list(self.bombs):
            for ship in list(self.ships):
                if ship["x"] < bomb.x < ship["x"] + 50 and ship["y"] < bomb.y < ship["y"] + 40:
                    # Помечаем корабль как "взрывающийся"
                    ship["exploding"] = True
                    ship["explosion_timer"] = 30  # Таймер взрыва

                    # Удаляем снаряд
                    self.bombs.remove(bomb)
                    break


    def update_explosions(self):
        for ship in list(self.ships):
            if ship.get("exploding"):
                ship["explosion_timer"] -= 1
                if ship["explosion_timer"] <= 0:
                    self.ships.remove(ship)  # Удаляем корабль после завершения взрыва


    def get_state(self):
        return {
            "ships": self.ships,
            "bombs": [{"x": bomb.x, "y": bomb.y} for bomb in self.bombs],
            "explosions": [{"x": ship["x"], "y": ship["y"]} for ship in self.ships if ship.get("exploding")],
            "gun": {
                "x": self.gun.x,
                "y": self.gun.y,
                "angle": self.gun.angle,
            },
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
