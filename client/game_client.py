import pygame
from client.rendering import Renderer
from client.handlers import ClientHandler
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT
from common.database import init_db, save_result, get_results


class GameClient:
    def __init__(self):
        self.handler = ClientHandler()
        self.renderer = Renderer()
        self.username = ""  # Имя пользователя
        self.space_pressed = False
        self.shots_fired = 0
        self.ships_destroyed = 0
        self.game_over = False
        init_db()  # Инициализация базы данных

    def main_screen(self, screen):
        font = pygame.font.Font(None, 74)
        input_box = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 25, 200, 50)
        color = pygame.Color('dodgerblue2')
        text = ""
        prompt = "Введите имя пользователя:"
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.username = text
                        return True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
            screen.fill((0, 0, 0))
            prompt_surface = font.render(prompt, True, (255, 255, 255))
            screen.blit(prompt_surface, (WINDOW_WIDTH // 2 - prompt_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
            txt_surface = font.render(text, True, color)
            screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
            pygame.draw.rect(screen, color, input_box, 2)
            pygame.display.flip()

    def main_menu(self, screen):
        font = pygame.font.Font(None, 74)
        menu_items = ["1. Play", "2. Results", "3. Change User"]
        while True:
            screen.fill((0, 0, 0))
            for i, item in enumerate(menu_items):
                text = font.render(item, True, (255, 255, 255))
                screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 200 + i * 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return "Play"
                    elif event.key == pygame.K_2:
                        return "Results"
                    elif event.key == pygame.K_3:
                        return "Change User"

    def show_results(self, screen):
        font = pygame.font.Font(None, 50)
        results = get_results(self.username)
        screen.fill((0, 0, 0))
        y_offset = 100
        for shots, destroyed in results:
            result_text = f"Shots: {shots}, Ships Destroyed: {destroyed}"
            text = font.render(result_text, True, (255, 255, 255))
            screen.blit(text, (50, y_offset))
            y_offset += 60
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    return True

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game Client")
        clock = pygame.time.Clock()

        if not self.main_screen(screen):
            pygame.quit()
            return

        while True:
            action = self.main_menu(screen)
            if action == "Play":
                self.play_game(screen, clock)
            elif action == "Results":
                self.show_results(screen)
            elif action == "Change User":
                if not self.main_screen(screen):
                    break

        pygame.quit()

    def play_game(self, screen, clock):
        self.shots_fired = 0
        self.ships_destroyed = 0
        self.game_over = False
        self.handler.send_reset_command()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            if self.game_over:
                self.display_game_over(screen, state.get("ships_destroyed", 0) )
                pygame.display.flip()
                save_result(self.username, self.shots_fired, state.get("ships_destroyed", 0))
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            return

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

            state = self.handler.get_state()

            self.renderer.render(
                screen,
                state.get("ships", []),
                state.get("gun", {}),
                state.get("bombs", []),
                state.get("explosions", [])
            )
            self.display_stats(screen, state.get("ships_destroyed", 0))
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()

    def display_stats(self, screen, ships_destroyed):
        font = pygame.font.Font(None, 36)
        stats_text = (
            f"Shots Fired: {self.shots_fired}  "
            f"Ships Destroyed: {ships_destroyed}"
        )
        text_surface = font.render(stats_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

    def display_game_over(self, screen, ships_destroyed):
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        stats = f"Shots: {self.shots_fired}, Ships Destroyed: {ships_destroyed}"
        stats_text = font.render(stats, True, (255, 255, 255))
        stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(stats_text, stats_rect)


if __name__ == "__main__":
    client = GameClient()
    client.run()
