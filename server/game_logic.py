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
        # Центрируем пушку
        self.gun = Gun(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)

    def generate_ships(self):
        """Создаёт новые корабли и обновляет их движение."""
        # Удаляем корабли, которые вышли за пределы поля или взорвались
        self.ships = [
            ship for ship in self.ships
            if not ship.get("out_of_bounds") and not ship.get("exploding")
        ]

        # Генерация новых кораблей
        if len(self.ships) < 2 and random.random() < 0.02:
            self.ships.append({
                "id": self.ship_id_counter,
                "x": -50,  # Начинаем за левым краем игрового поля
                "y": random.randint(50, WINDOW_HEIGHT // 2),  # Центрируем по вертикали
                "speed": random.uniform(*SHIP_SPEED_RANGE),
                "base_y": random.randint(50, WINDOW_HEIGHT // 2),  # Базовая высота для синусоиды
                "out_of_bounds": False,
                "exploding": False,
                "explosion_timer": 0,
                "wave_offset": random.uniform(0, math.pi * 2),  # Сдвиг фазы синусоиды
            })
            self.ship_id_counter += 1

        for ship in self.ships:
            # Лёгкое изменение скорости
            if random.random() < 0.1:  # 10% вероятность небольшого изменения скорости
                ship["speed"] += random.uniform(-0.1, 0.1)
                ship["speed"] = max(0.5, min(ship["speed"], max(SHIP_SPEED_RANGE)))

            # Движение по синусоиде
            ship["y"] = ship["base_y"] + math.sin(ship["x"] * 0.02 + ship["wave_offset"]) * 10

            # Обновляем положение корабля
            ship["x"] += ship["speed"] * 0.008
            if ship["x"] >= WINDOW_WIDTH:  # Корабль вышел за правую границу поля
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
        self.speed = 2  # Скорость бомбы

    def move(self):
        self.x += self.speed/200 * math.cos(math.radians(self.angle))
        self.y -= self.speed/200 * math.sin(math.radians(self.angle))

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT