import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c
import pytest
# Инициализация pygame
pg.init()

# Создаем объект clock
clock = pg.time.Clock()

# Создаем игровое окно
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

# Игровые переменные
game_over = False
game_outcome = 0  # -1 это поражение, 1 это победа
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None

# Загрузка изображений
# Карта
map_image = pg.image.load('levels/level.png').convert_alpha()
# Спрайты турелей
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)
# Изображение турели для курсора мыши
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
# Враги
enemy_images = {
    "weak": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
    "medium": pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
    "strong": pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
    "elite": pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
}
# Кнопки
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
# Элементы интерфейса
heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()

# Загрузка звуков
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)

# Загрузка данных уровня из JSON файла
with open('levels/level.tmj') as file:
    world_data = json.load(file)

# Загрузка шрифтов для отображения текста на экране
text_font = pg.font.SysFont("Consolas", 24, bold=True)
large_font = pg.font.SysFont("Consolas", 36)

def draw_text(text, font, text_col, x, y):
    """
    Отрисовка текста на экране.

    Args:
        text (str): Текст для отображения.
        font (pygame.font.Font): Шрифт для текста.
        text_col (str): Цвет текста.
        x (int): Координата X для размещения текста.
        y (int): Координата Y для размещения текста.
    """
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def display_data():
    """
    Отображение игровой информации (например, уровень, здоровье, деньги) на боковой панели.
    """
    # Рисуем панель
    pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
    # Отображаем данные
    draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
    screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
    draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
    draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)

def create_turret(mouse_pos):
    """
    Создание турели в указанной позиции мыши, если тайл подходит.

    Args:
        mouse_pos (tuple): Позиция мыши (x, y).
    """
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    # Вычисляем последовательный номер тайла
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    # Проверяем, является ли тайл травой
    if world.tile_map[mouse_tile_num] == 7:
        # Проверяем, что на этом тайле нет другой турели
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        # Если место свободно, создаем турель
        if space_is_free:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
            turret_group.add(new_turret)
            # Вычитаем стоимость турели
            world.money -= c.BUY_COST

def select_turret(mouse_pos):
    """
    Выбор турели в указанной позиции мыши.

    Args:
        mouse_pos (tuple): Позиция мыши (x, y).

    Returns:
        Turret: Объект выбранной турели или None, если турель не выбрана.
    """
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret

def initialize_game():
    """
        Инициализирует игровую среду для Tower Defence.

        Осуществляет следующие действия:
        1. Инициализирует Pygame и устанавливает окно игры.
        2. Создает игровой мир на основе данных уровня.
        3. Загружает карту, обрабатывает данные уровня и врагов.
        4. Инициализирует группы спрайтов для турелей и врагов.

        Глобальные переменные:
        - world (World): Объект игрового мира.
        - screen (pygame.Surface): Экран для отображения игры.
        - turret_group (pygame.sprite.Group): Группа спрайтов турелей.
        - enemy_group (pygame.sprite.Group): Группа спрайтов врагов.
        - clock (pygame.time.Clock): Объект для управления временем в игре.

        Raises:
            FileNotFoundError: Если отсутствует файл уровня ('levels/level.tmj') или карта ('levels/level.png').
        """
    global world, screen, turret_group, enemy_group, clock
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.display.set_caption("Tower Defence")
    with open('levels/level.tmj') as file:
        world_data = json.load(file)
    map_image = pg.image.load('levels/level.png').convert_alpha()
    world = World(world_data, map_image)
    world.process_data()
    world.process_enemies()
    turret_group = pg.sprite.Group()
    enemy_group = pg.sprite.Group()


def clear_selection():
    """
    Снятие выделения со всех турелей.
    """
    for turret in turret_group:
        turret.selected = False

# Создаем мир
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

# Создаем группы
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

# Создаем кнопки
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)

# Игровой цикл
run = True
while run:
    clock.tick(c.FPS)

    #########################
    # ОБНОВЛЕНИЕ
    #########################

    if not game_over:
        # Проверяем, проиграл ли игрок
        if world.health <= 0:
            game_over = True
            game_outcome = -1  # Поражение
        # Проверяем, выиграл ли игрок
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1  # Победа

        # Обновляем группы
        enemy_group.update(world)
        turret_group.update(enemy_group, world)

        # Подсвечиваем выбранную турель
        if selected_turret:
            selected_turret.selected = True

    #########################
    # РИСОВАНИЕ
    #########################

    # Рисуем уровень
    world.draw(screen)

    # Рисуем группы
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data()

    if not game_over:
        # Проверяем, начался ли уровень
        if not level_started:
            if begin_button.draw(screen):
                level_started = True
        else:
            # Опция ускорения игры
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2
            # Создаем врагов
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        # Проверяем, завершена ли волна
        if world.check_level_complete():
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()

        # Рисуем кнопки
        draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
        if turret_button.draw(screen):
            placing_turrets = True
        if placing_turrets:
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= c.SCREEN_WIDTH:
                screen.blit(cursor_turret, cursor_rect)
            if cancel_button.draw(screen):
                placing_turrets = False
        if selected_turret:
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
                screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST
    else:
        pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius=30)
        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)
        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            enemy_group.empty()
            turret_group.empty()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                selected_turret = None
                clear_selection()
                if placing_turrets:
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)

    pg.display.flip()

pg.quit()
