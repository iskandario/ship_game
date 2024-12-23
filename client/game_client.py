import pygame
from client.rendering import Renderer
from client.handlers import ClientHandler
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT
from common.database import init_db, save_result, get_top_scores




class GameClient:
    def __init__(self):
        self.handler = ClientHandler()
        self.renderer = Renderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.username = ""  # Имя пользователя
        self.space_pressed = False
        self.shots_fired = 0
        self.ships_destroyed = 0
        self.game_over = False
        init_db()  # Инициализация базы данных

    def main_screen(self, screen):
        font = pygame.font.Font(None, 74)
        input_box = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 25, 300, 50)
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
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(screen, color, input_box, 2)
            pygame.display.flip()

    def show_top_scores(self, screen):
        """Отображает экран с таблицей лидеров."""
        font = pygame.font.Font(None, 74)
        small_font = pygame.font.Font(None, 36)
        title_text = "Top Scores"
        title_surface = font.render(title_text, True, (255, 255, 255))
        
        # Получаем результаты из базы данных
        top_scores = get_top_scores()

        while True:
            screen.fill((0, 0, 0))
            # Рисуем заголовок
            screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 50))
            
            # Отображаем топ-результаты
            for i, score in enumerate(top_scores[:10]):  # Ограничиваем до 10 результатов
                # Пытаемся распаковать данные в две переменные
                try:
                    username, max_destroyed = score
                    text = f"{i + 1}. {username}: {max_destroyed} destroyed"
                except ValueError:
                    # Если данных недостаточно, отображаем "-"
                    username = score[0]
                    text = f"{i + 1}. {username}: - destroyed"
                
                score_surface = small_font.render(text, True, (255, 255, 255))
                screen.blit(score_surface, (50, 150 + i * 40))

            # Инструкция по выходу
            exit_text = "Press any key to return to menu"
            exit_surface = small_font.render(exit_text, True, (255, 255, 255))
            screen.blit(exit_surface, (WINDOW_WIDTH // 2 - exit_surface.get_width() // 2, WINDOW_HEIGHT - 50))

            pygame.display.flip()

            # Обрабатываем события
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    return  # Выход в главное меню




    def main_menu(self, screen):
        font = pygame.font.Font(None, 74)
        title_font = pygame.font.Font(None, 100)
        menu_items = ["1. Play", "2. Top Scores", "3. Change User", "4. Exit"]

        # Разноцветное название игры
        title = "PIRATE GUN"
        title_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]
        while True:
            screen.fill((0, 0, 0))

            # Рисуем разноцветное название игры
            x_offset = WINDOW_WIDTH // 2 - len(title) * 30
            for i, letter in enumerate(title):
                letter_surface = title_font.render(letter, True, title_colors[i % len(title_colors)])
                screen.blit(letter_surface, (x_offset + i * 60, 50))

            # Рисуем пункты меню
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
                        return "Top Scores"
                    elif event.key == pygame.K_3:
                        return "Change User"
                    elif event.key == pygame.K_4:
                        return "Exit"

    def play_game(self, screen, clock):
        self.shots_fired = 0
        self.ships_destroyed = 0
        self.game_over = False
        self.handler.send_reset_command()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Обработка клавиши ESC
                        return

            state = self.handler.get_state()
            self.game_over = self.shots_fired >= 10 and len(state.get("bombs", [])) == 0

            if self.game_over:
                self.display_game_over(screen, state.get("ships_destroyed", 0))
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
            else:
                self.space_pressed = False

            self.renderer.render(
                screen,
                state.get("ships", []),
                state.get("gun", {}),
                state.get("bombs", []),
                state.get("explosions", [])
            )
            self.display_stats(screen, state.get("ships_destroyed", 0))
            self.display_hints(screen)  # Подсказки
            pygame.display.flip()
            clock.tick(60)

    def display_stats(self, screen, ships_destroyed):
        font = pygame.font.Font(None, 36)
        stats_text = (
            f"Shots Fired: {self.shots_fired}  "
            f"Ships Destroyed: {ships_destroyed}"
        )
        text_surface = font.render(stats_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

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
            elif action == "Top Scores":
                self.show_top_scores(screen)
            elif action == "Change User":
                if not self.main_screen(screen):
                    break
            elif action == "Exit":
                break

    pygame.quit()
    def display_hints(self, screen):
        font = pygame.font.Font(None, 36)
        hints = [
            "SPACE - Fire",
            "LEFT/RIGHT - Move Gun",
            "ESC - Exit to Menu",
        ]
        y_offset = WINDOW_HEIGHT - 100
        for hint in hints:
            hint_surface = font.render(hint, True, (255, 255, 255))
            screen.blit(hint_surface, (WINDOW_WIDTH - 300, y_offset))
            y_offset += 30

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