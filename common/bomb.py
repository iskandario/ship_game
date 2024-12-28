import math
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT

class Bomb:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 2.3  # Скорость бомбы

    def move(self):
        self.x += self.speed / 200 * math.cos(math.radians(self.angle))
        self.y -= self.speed / 200 * math.sin(math.radians(self.angle))

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT