import logging
from common.gun import Gun
import random
import math
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT, SHIP_Y_RANGE, SHIP_SPEED_RANGE

# Настраиваем логгер
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GameLogic:
    def __init__(self):
        self.ships = []
        self.bombs = []
        self.ship_id_counter = 1
        self.gun = Gun(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 70)
        self.explosions = []  # Отдельный список для взрывов

    def generate_ships(self):
        """Генерация кораблей."""
        if len(self.ships) < 2 and random.random() < 0.02:
            ship = {
                "id": self.ship_id_counter,
                "x": -50,
                "y": random.randint(*SHIP_Y_RANGE),
                "speed": random.uniform(*SHIP_SPEED_RANGE),
            }
            self.ships.append(ship)
            self.ship_id_counter += 1
            logger.info(f"Ship generated: {ship}")

        for ship in self.ships:
            ship["x"] += ship["speed"] * 0.005

        # Удаляем корабли, вышедшие за экран
        removed_ships = [ship for ship in self.ships if ship["x"] >= WINDOW_WIDTH]
        if removed_ships:
            logger.info(f"Ships removed (out of screen): {removed_ships}")

        self.ships = [ship for ship in self.ships if ship["x"] < WINDOW_WIDTH]

    def update_gun(self, command):
        """Обновляет угол поворота пушки на основе команды."""
        if command == "move_left":
            self.gun.rotate("left")
            logger.info("Gun moved left")
        elif command == "move_right":
            self.gun.rotate("right")
            logger.info("Gun moved right")

    def fire_bomb(self):
        """Создание снаряда при выстреле."""
        tip_x, tip_y = self.gun.get_tip_position()  # Конец дула пушки
        bomb = Bomb(tip_x, tip_y, self.gun.angle)
        self.bombs.append(bomb)
        logger.info(f"Bomb fired: {bomb}")

    def update_bombs(self):
        """Обновляет положение снарядов."""
        for bomb in self.bombs:
            bomb.move()
        removed_bombs = [bomb for bomb in self.bombs if bomb.is_out_of_bounds()]
        if removed_bombs:
            logger.info(f"Bombs removed (out of bounds): {removed_bombs}")

        self.bombs = [bomb for bomb in self.bombs if not bomb.is_out_of_bounds()]

    def check_collisions(self):
        """Проверяет попадания снарядов по кораблям."""
        for bomb in list(self.bombs):
            for ship in list(self.ships):
                if ship["x"] < bomb.x < ship["x"] + 50 and ship["y"] < bomb.y < ship["y"] + 40:
                    # Добавляем взрыв
                    explosion = {"id": ship["id"], "x": ship["x"], "y": ship["y"], "timer": 30}
                    self.explosions.append(explosion)
                    logger.info(f"Collision detected: {explosion}")

                    # Удаляем корабль и снаряд
                    self.ships.remove(ship)
                    self.bombs.remove(bomb)
                    logger.info(f"Ship destroyed: {ship}")
                    break

    def update_explosions(self):
        """Обновляет состояние взрывов."""
        for explosion in list(self.explosions):
            explosion["timer"] -= 1
            if explosion["timer"] <= 0:
                logger.info(f"Explosion removed: {explosion}")
                self.explosions.remove(explosion)

    def get_state(self):
        """Возвращает текущее состояние игры."""
        return {
            "ships": self.ships,
            "bombs": [{"x": bomb.x, "y": bomb.y} for bomb in self.bombs],
            "explosions": self.explosions,
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
        self.x += self.speed / 200 * math.cos(math.radians(self.angle))
        self.y -= self.speed / 200 * math.sin(math.radians(self.angle))

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT

    def __repr__(self):
        return f"Bomb(x={self.x:.2f}, y={self.y:.2f}, angle={self.angle})"
