import pygame
from client.rendering import Renderer
from client.handlers import ClientHandler
from common.config import WINDOW_WIDTH, WINDOW_HEIGHT


class GameClient:
    def __init__(self):
        self.handler = ClientHandler()
        self.renderer = Renderer()
        self.space_pressed = False  # Флаг для отслеживания нажатия пробела
        self.shots_fired = 0        # Счетчик выстрелов
        self.ships_destroyed = 0    # Счетчик сбитых кораблей
        self.game_over = False      # Флаг завершения игры

    def display_game_over(self, screen):
        """Отображает экран завершения игры."""
        # Установка шрифта
        font = pygame.font.Font(None, 74)

        # Отображение текста "Game Over"
        text = font.render("Game Over", True, (255, 0, 0))  # Красный текст
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        # Отображение статистики: выстрелы и сбитые корабли
        stats = f"Shots: {self.shots_fired}, Ships Destroyed: {self.ships_destroyed}"
        stats_text = font.render(stats, True, (255, 255, 255))  # Белый текст
        stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(stats_text, stats_rect)


    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Клиент")
        clock = pygame.time.Clock()

        previous_ships = set()  # Хранит идентификаторы кораблей из предыдущего состояния
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Завершение игры, если достигнут лимит выстрелов
            if self.game_over:
                self.display_game_over(screen)  # Отображение результатов
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()

            # Управление пушкой
            if keys[pygame.K_LEFT]:
                self.handler.send_gun_command("move_left")
            if keys[pygame.K_RIGHT]:
                self.handler.send_gun_command("move_right")

            # Выстрел из пушки
            if keys[pygame.K_SPACE]:
                if not self.space_pressed and self.shots_fired < 100:
                    self.handler.send_fire_command()  # Отправляем команду "выстрел"
                    self.space_pressed = True
                    self.shots_fired += 1  # Увеличиваем счетчик выстрелов
                if self.shots_fired >= 100:
                    self.game_over = True  # Устанавливаем флаг завершения игры
            else:
                self.space_pressed = False  # Сбрасываем флаг, когда клавиша отпущена

            # Получение состояния игры
            state = self.handler.get_state()
            current_ships = {ship["id"] for ship in state.get("ships", [])}  # Уникальные идентификаторы кораблей

            # Вычисляем количество уничтоженных кораблей
            destroyed_ships = previous_ships - current_ships
            self.ships_destroyed += len(destroyed_ships)
            previous_ships = current_ships

            # Отрисовка
            self.renderer.render(
                screen,
                state.get("ships", []),
                state.get("gun", {}),
                state.get("bombs", []),
                state.get("explosions", [])
            )
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    client = GameClient()
    client.run()