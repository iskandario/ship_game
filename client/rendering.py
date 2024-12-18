import pygame
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT
from resources import load_assets


class Renderer:
    def __init__(self):
        self.assets = load_assets()
        self.background = pygame.transform.scale(self.assets["background"], (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.ship_image = pygame.transform.scale(self.assets["ship"], (50, 40))
        self.gun_image = pygame.transform.scale(self.assets["gun"], (70, 140))

    def render(self, screen, ships, gun_state):
        screen.blit(self.background, (0, 0))
        for ship in ships:
            screen.blit(self.ship_image, (ship["x"], ship["y"]))

        gun_angle = gun_state["angle"]
        gun_x, gun_y = gun_state["x"], gun_state["y"]
        rotated_gun = pygame.transform.rotate(self.gun_image, gun_angle - 90)
        gun_rect = rotated_gun.get_rect(center=(gun_x, gun_y))
        screen.blit(rotated_gun, gun_rect.topleft)