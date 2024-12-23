import pygame
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT
from resources import load_assets


class Renderer:
    def __init__(self, window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT):
        self.assets = load_assets()
        self.window_width = window_width
        self.window_height = window_height

        # Масштабируем элементы под размеры окна
        self.background = pygame.transform.scale(self.assets["background"], (self.window_width, self.window_height))
        self.ship_image = pygame.transform.scale(self.assets["ship"], (50, 40))
        self.gun_image = pygame.transform.scale(self.assets["gun"], (70, 140))
        self.bomb_image = pygame.transform.scale(self.assets["bomb"], (20, 20))
        self.boom_image = pygame.transform.scale(self.assets["boom"], (80, 40))

    def render(self, screen, ships, gun_state, bombs, explosions):
        screen.blit(self.background, (0, 0))  # Отрисовка фона

        # Отрисовка кораблей
        for ship in ships:
            screen.blit(self.ship_image, (ship["x"], ship["y"]))

        # Отрисовка снарядов
        for bomb in bombs:
            screen.blit(self.bomb_image, (bomb["x"], bomb["y"]))

        # Отрисовка взрывов
        for explosion in explosions:
            screen.blit(self.boom_image, (explosion["x"], explosion["y"]))

        # Отрисовка пушки
        gun_angle = gun_state["angle"]
        gun_x, gun_y = gun_state["x"], gun_state["y"]
        rotated_gun = pygame.transform.rotate(self.gun_image, gun_angle - 90)
        gun_rect = rotated_gun.get_rect(center=(gun_x, gun_y))
        screen.blit(rotated_gun, gun_rect.topleft)