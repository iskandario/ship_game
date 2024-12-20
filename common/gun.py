import math


class Gun:
    def __init__(self, x, y, angle=90):
        self.x = x
        self.y = y
        self.angle = angle

    def rotate(self, direction):
        """Поворачивает пушку влево или вправо."""
        if direction == "left" and self.angle < 180:
            self.angle += 2
        elif direction == "right" and self.angle > 0:
            self.angle -= 2

    def get_tip_position(self):
        """Возвращает координаты конца пушки."""
        angle_rad = math.radians(self.angle)
        tip_x = self.x + 70 * math.cos(angle_rad)
        tip_y = self.y - 70 * math.sin(angle_rad)
        return tip_x, tip_y
