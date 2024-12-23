from common.gun import Gun
import random
import math
import time
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT, SHIP_Y_RANGE, SHIP_SPEED_RANGE


class GameLogic:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Сбрасывает состояние игры для новой сессии."""
        self.ships = []
        self.bombs = []
        self.explosions = [] 
        self.ship_id_counter = 1
        self.ships_destroyed = 0
        self.shots_fired = 0  
        self.game_over_timer = 0  # Таймер для завершения игры
        self.last_explosion_time = 0 
        # Центрируем пушку
        self.gun = Gun(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.game_over_timer = 0  # Таймер для завершения игры

    def generate_ships(self):
        """Создаёт новые корабли и обновляет их движение."""
        # Удаляем корабли, которые вышли за пределы поля
        self.ships = [
            ship for ship in self.ships
            if not ship.get("out_of_bounds")
        ]

        # Генерация новых кораблей
        if len(self.ships) < 2 and random.random() < 0.02:
            self.ships.append({
                "id": self.ship_id_counter,
                "x": -50,  # Начинаем за левым краем игрового поля
                "y": random.randint(WINDOW_HEIGHT // 4, WINDOW_HEIGHT // 2),  # Генерация в нижней части верхней половины экрана
                "speed": random.uniform(*SHIP_SPEED_RANGE),
                "base_y": random.randint(WINDOW_HEIGHT // 4, WINDOW_HEIGHT // 2),  # Базовая высота для синусоиды
                "out_of_bounds": False,
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

    def update_explosions(self):
        current_time = time.time()
        self.explosions = [
            explosion for explosion in self.explosions
            if current_time - explosion["created_at"] < 1.0  # Удаляем через 1 секунду
        ]

    def check_collisions(self):
        for bomb in list(self.bombs):
            for ship in list(self.ships):
                if ship["x"] < bomb.x < ship["x"] + 50 and ship["y"] < bomb.y < ship["y"] + 40:
                    # Добавляем взрыв и обновляем время последнего взрыва
                    self.explosions.append({"x": ship["x"], "y": ship["y"], "created_at": time.time()})
                    self.last_explosion_time = time.time()  # Обновляем время последнего взрыва
                    self.bombs.remove(bomb)
                    self.ships.remove(ship)
                    self.ships_destroyed += 1
                    break

    def is_game_over(self):
        """Проверяет, завершена ли игра с задержкой."""
        # Игра завершена только после последнего взрыва
        if self.shots_fired >= 10 and len(self.explosions) == 0:
            # Если прошел достаточно времени после последнего взрыва
            if time.time() - self.last_explosion_time > 1:
                return True
        return False


    def get_state(self):
        return {
            "ships": self.ships,
            "bombs": [{"x": bomb.x, "y": bomb.y} for bomb in self.bombs],
            "explosions": [{"x": explosion["x"], "y": explosion["y"]} for explosion in self.explosions],
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
        self.x += self.speed / 200 * math.cos(math.radians(self.angle))
        self.y -= self.speed / 200 * math.sin(math.radians(self.angle))

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT