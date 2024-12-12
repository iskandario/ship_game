import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Конфигурация окна
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Морская стрелялка")
clock = pygame.time.Clock()

# Загрузка ассетов
background_img = pygame.image.load("assets/fon.png")
gun_img = pygame.image.load("assets/gun.png")
bomb_img = pygame.image.load("assets/bomb.png")
ship_img = pygame.image.load("assets/ship.png")
boom_img = pygame.image.load("assets/boom.png")

# Параметры игры
GUN_CENTER = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 70)  # Центр пушки
GUN_ROTATION_SPEED = 2  # Скорость поворота пушки
BOMB_SPEED = 10  # Скорость бомбы
SHIP_SPEED_RANGE = (2, 5)  # Диапазон скорости кораблей
SHIP_Y_RANGE = (WINDOW_HEIGHT // 4, WINDOW_HEIGHT // 3 + 50)  # Новый диапазон высоты кораблей
EXPLOSION_DURATION = 60  # Время эффекта взрыва (в кадрах)
MAX_BOMBS = 10  # Максимальное количество бомб

# Переменные состояния
score = 0
remaining_bombs = MAX_BOMBS
explosions = []

# Классы
class Gun:
    def __init__(self):
        self.angle = 60  # Начальный угол пушки (60 градусов)
        self.image = pygame.transform.scale(gun_img, (70, 140))
        self.rect = self.image.get_rect(center=GUN_CENTER)

    def draw(self):
        # Поворот изображения пушки
        rotated_image = pygame.transform.rotate(self.image, self.angle - 90)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)

    def rotate(self, direction):
        # Ограничение угла поворота
        if direction == "left" and self.angle < 180:
            self.angle += GUN_ROTATION_SPEED
        elif direction == "right" and self.angle > 0:
            self.angle -= GUN_ROTATION_SPEED

    def get_tip_position(self):
        # Возвращает координаты конца дула пушки
        angle_rad = math.radians(self.angle)
        tip_x = GUN_CENTER[0] + 70 * math.cos(angle_rad)  # Увеличить для корректного конца дула
        tip_y = GUN_CENTER[1] - 70 * math.sin(angle_rad)
        return tip_x, tip_y


class Bomb:
    def __init__(self, x, y, angle, speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed  # Скорость теперь задается динамически
        self.image = pygame.transform.scale(bomb_img, (20, 20))

    def move(self):
        # Перемещение бомбы в направлении угла
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = EXPLOSION_DURATION  # Время жизни взрыва

    def draw(self):
        screen.blit(pygame.transform.scale(boom_img, (80, 40)), (self.x, self.y))

    def update(self):
        self.timer -= 1
        return self.timer <= 0  # True, если взрыв завершён
    
class Ship:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.image = pygame.transform.scale(ship_img, (65, 50))
        self.exploding = False
        self.explosion_timer = 0

    def move(self):
        if not self.exploding:
            self.x += self.speed

    def draw(self):
        if self.exploding:
            screen.blit(pygame.transform.scale(boom_img, (80, 40)), (self.x, self.y))
        else:
            screen.blit(self.image, (self.x, self.y))

    def start_explosion(self):
        self.exploding = True
        self.explosion_timer = EXPLOSION_DURATION

    def update_explosion(self):
        if self.exploding:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                return True  # Указывает, что корабль можно удалить
        return False

fire_power = 0  # Текущая сила выстрела
max_fire_power = 100  # Максимальная сила выстрела
space_pressed = False  # Указывает, нажата ли клавиша пробела

def draw_fire_power():
    segments = 10  # Количество делений
    segment_width = 15  # Ширина одного деления
    segment_height = 10  # Высота одного деления
    spacing = 5  # Расстояние между делениями

    x = 20  # Позиция шкалы (слева от экрана)
    y = WINDOW_HEIGHT - 60  # Расположение над индикатором патронов

    # Подсчет количества активных делений
    active_segments = int((fire_power / max_fire_power) * segments)

    for i in range(segments):
        # Расчет цвета: от зеленого (0,255,0) к красному (255,0,0)
        ratio = i / (segments - 1)  # Нормализация индекса сегмента
        color = (
            int(255 * ratio),       # Красный увеличивается
            int(255 * (1 - ratio)), # Зеленый уменьшается
            0                       # Синий остается 0
        )
        # Если сегмент активен, рисуем цвет, иначе серый
        draw_color = color if i < active_segments else (50, 50, 50)

        pygame.draw.rect(
            screen,
            draw_color,
            (x + i * (segment_width + spacing), y, segment_width, segment_height)
        )

pirate_img = pygame.image.load("assets/pirate.png")
pirate_img = pygame.transform.scale(pirate_img, (70, 70))  # Уменьшаем размер для компактного отображения

# Добавляем функцию для отрисовки пирата
def draw_pirate():
    pirate_x = GUN_CENTER[0] - 180  # Позиция справа от пушки
    pirate_y = GUN_CENTER[1] - 20  # На уровне пушки
    screen.blit(pirate_img, (pirate_x, pirate_y))

# Инициализация игровых объектов
gun = Gun()
bombs = []
ships = []

# Генерация кораблей
def spawn_ship():
    y = random.randint(*SHIP_Y_RANGE)
    speed = random.randint(*SHIP_SPEED_RANGE)
    ship = Ship(-100, y, speed)
    ships.append(ship)

# Отображение оставшихся бомб
def draw_bombs():
    for i in range(remaining_bombs):
        screen.blit(pygame.transform.scale(bomb_img, (15, 15)), (20 + i * 20, WINDOW_HEIGHT - 40))

# Основной игровой цикл
frame_counter = 0
running = True
while running:
    screen.blit(pygame.transform.scale(background_img, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True  # Указываем, что пробел нажат
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and space_pressed:
                space_pressed = False  # Пробел отпущен
                # Создаем бомбу с учетом силы выстрела
                angle = gun.angle
                bomb_x = GUN_CENTER[0] + 25 * math.cos(math.radians(angle))
                bomb_y = GUN_CENTER[1] - 25 * math.sin(math.radians(angle))
                speed = 2 + (fire_power / max_fire_power) * 20  # Минимальная скорость 5, максимальная 20
                bomb = Bomb(bomb_x, bomb_y, angle, speed)
                bombs.append(bomb)
                remaining_bombs -= 1
                fire_power = 0  # Сброс силы выстрела
 


    # Управление пушкой
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        gun.rotate("left")
    if keys[pygame.K_RIGHT]:
        gun.rotate("right")

    if space_pressed:
        fire_power += 1
        fire_power = min(fire_power, max_fire_power)


    # Обновление бомб
    for bomb in bombs[:]:
        bomb.move()
        bomb.draw()
        if bomb.is_out_of_bounds():
            bombs.remove(bomb)

    # Обновление кораблей
    for ship in ships[:]:
        ship.move()
        ship.draw()

        # Проверка столкновения с бомбой
        for bomb in bombs[:]:
            ship_rect = pygame.Rect(ship.x, ship.y, 80, 40)
            bomb_rect = pygame.Rect(bomb.x, bomb.y, 20, 20)
            if ship_rect.colliderect(bomb_rect):
                explosions.append(Explosion(ship.x, ship.y)) 
                ships.remove(ship)  # Удаляем корабль
                bombs.remove(bomb)  # Удаляем бомбу
                score += 1
                break

        for explosion in explosions[:]:
         explosion.draw()
         if explosion.update():  # Удаляем завершённый взрыв
            explosions.remove(explosion)

    draw_fire_power()
         

    # Поворот и отрисовка пушки
    gun.draw()
    draw_pirate()

    # Отображение оставшихся бомб
    draw_bombs()

    # Спавн кораблей с интервалом
    if frame_counter % 120 == 0:
        spawn_ship()

    # Завершение игры
    if remaining_bombs == 0 and not bombs:
        running = False

    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)
    frame_counter += 1

# Конец игры
print(f"Игра окончена! Ваш счёт: {score}")
pygame.quit()
sys.exit()