import pygame
from client.rendering import Renderer
from client.handlers import ClientHandler
from common.database import get_or_create_user, save_result, get_results
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT


class GameClient:
    def __init__(self):
        self.handler = ClientHandler()
        self.renderer = Renderer()
        self.state = "enter_name"  # Возможные состояния: enter_name, menu, game, results
        self.username = ""
        self.user_id = None
        self.input_text = ""
        self.space_pressed = False
        self.shots_fired = 0
        self.ships_destroyed = 0
        self.game_over = False

    def display_text(self, screen, text, position, font_size=36, color=(255, 255, 255)):
        """Вспомогательный метод для отображения текста на экране."""
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)

    def display_game_over(self, screen):
        """Отображает экран завершения игры."""
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        stats = f"Shots: {self.shots_fired}, Ships Destroyed: {self.ships_destroyed}"
        stats_text = font.render(stats, True, (255, 255, 255))
        stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(stats_text, stats_rect)

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.input_text.strip():
                self.username = self.input_text.strip()
                self.user_id = get_or_create_user(self.username)
                self.state = "menu"
                self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode

    def display_menu(self, screen):
        self.display_text(screen, f"Welcome, {self.username}!", (WINDOW_WIDTH // 2, 100))
        self.display_text(screen, "1. Play", (WINDOW_WIDTH // 2, 200))
        self.display_text(screen, "2. Results", (WINDOW_WIDTH // 2, 300))
        self.display_text(screen, "3. Change User", (WINDOW_WIDTH // 2, 400))

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.state = "game"
                self.shots_fired = 0
                self.ships_destroyed = 0
                self.game_over = False
            elif event.key == pygame.K_2:
                self.state = "results"
            elif event.key == pygame.K_3:
                self.state = "enter_name"

    def display_results(self, screen):
        self.display_text(screen, f"Results for {self.username}:", (WINDOW_WIDTH // 2, 100))
        results = get_results(self.user_id)
        y_offset = 150
        for shots, destroyed in results:
            self.display_text(screen, f"Shots: {shots}, Destroyed: {destroyed}", (WINDOW_WIDTH // 2, y_offset))
            y_offset += 50
        self.display_text(screen, "Press any key to return", (WINDOW_WIDTH // 2, 500), font_size=24)

    def handle_results_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.state = "menu"

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ship Game")
        clock = pygame.time.Clock()
        running = True

        previous_ships = set()

        while running:
            screen.fill((0, 0, 0))  # Очищаем экран

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Обработка событий
                if self.state == "enter_name":
                    self.handle_name_input(event)
                elif self.state == "menu":
                    self.handle_menu_input(event)
                elif self.state == "results":
                    self.handle_results_input(event)
                elif self.state == "game" and self.game_over:
                    if event.type == pygame.KEYDOWN:
                        self.state = "menu"
                        save_result(self.user_id, self.shots_fired, self.ships_destroyed)

            # Отрисовка в зависимости от состояния
            if self.state == "enter_name":
                self.display_text(screen, "Enter your name:", (WINDOW_WIDTH // 2, 200))
                self.display_text(screen, self.input_text, (WINDOW_WIDTH // 2, 300))
            elif self.state == "menu":
                self.display_menu(screen)
            elif self.state == "results":
                self.display_results(screen)
            elif self.state == "game":
                if self.game_over:
                    self.display_game_over(screen)
                else:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        self.handler.send_gun_command("move_left")
                    if keys[pygame.K_RIGHT]:
                        self.handler.send_gun_command("move_right")
                    if keys[pygame.K_SPACE]:
                        if not self.space_pressed and self.shots_fired < 10:
                            self.handler.send_fire_command()
                            self.space_pressed = True
                            self.shots_fired += 1
                        if self.shots_fired >= 10:
                            self.game_over = True
                    else:
                        self.space_pressed = False

                    # Получение состояния игры
                    state = self.handler.get_state()

                    # Подсчет уничтоженных кораблей
                    for explosion in state.get("explosions", []):
                        if explosion["id"] not in previous_ships:
                            self.ships_destroyed += 1
                            previous_ships.add(explosion["id"])

                    # Рендеринг элементов игры
                    self.renderer.render(
                        screen,
                        state.get("ships", []),
                        state.get("gun", {}),
                        state.get("bombs", []),
                        state.get("explosions", [])
                    )

            pygame.display.flip()  # Обновляем экран
            clock.tick(60)  # Ограничиваем FPS

        pygame.quit()


if __name__ == "__main__":
    client = GameClient()
    client.run()
