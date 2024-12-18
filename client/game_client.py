import pygame
from client.rendering import Renderer
from client.handlers import ClientHandler
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT


class GameClient:
    def __init__(self):
        self.handler = ClientHandler()
        self.renderer = Renderer()

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Клиент")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.handler.send_gun_command("move_left")
            if keys[pygame.K_RIGHT]:
                self.handler.send_gun_command("move_right")

            state = self.handler.get_state()  # Получаем текущее состояние (ships + gun)

            # Отрисовка
            self.renderer.render(screen, state["ships"], state["gun"])
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    client = GameClient()
    client.run()