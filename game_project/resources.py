import pygame

def load_assets():
    return {
        "background": pygame.image.load("assets/fon.png"),
        "gun": pygame.image.load("assets/gun.png"),
        "bomb": pygame.image.load("assets/bomb.png"),
        "ship": pygame.image.load("assets/ship.png"),
        "boom": pygame.image.load("assets/boom.png"),
        "pirate": pygame.image.load("assets/pirate.png"),
    }