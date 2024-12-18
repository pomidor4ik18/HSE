import pygame as pg
import random
import constants as c
from enemy_data import ENEMY_SPAWN_DATA

class World():
    """
    Представляет игровой мир, включая данные уровня, управление врагами и состояние игры.
    """

    def __init__(self, data, map_image):
        """
        Инициализация объекта игрового мира.

        Args:
            data (dict): JSON-данные уровня, включая тайлмап и точки пути.
            map_image (pygame.Surface): Фоновое изображение карты.
        """
        self.level = 1
        self.game_speed = 1
        self.health = c.HEALTH
        self.money = c.MONEY
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0

    def process_data(self):
        """
        Извлечение информации о тайлмапе и точках пути из данных уровня.
        """
        for layer in self.level_data["layers"]:
            if layer["name"] == "tilemap":
                self.tile_map = layer["data"]
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    waypoint_data = obj["polyline"]
                    self.process_waypoints(waypoint_data)

    def process_waypoints(self, data):
        """
        Извлечение отдельных координат x и y из данных точек пути.

        Args:
            data (list): Список словарей точек пути, содержащих ключи "x" и "y".
        """
        for point in data:
            temp_x = point.get("x")
            temp_y = point.get("y")
            self.waypoints.append((temp_x, temp_y))

    def process_enemies(self):
        """
        Генерация случайного списка врагов для текущего уровня на основе данных появления.
        """
        enemies = ENEMY_SPAWN_DATA[self.level - 1]
        for enemy_type in enemies:
            enemies_to_spawn = enemies[enemy_type]
            for _ in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)
        random.shuffle(self.enemy_list)

    def check_level_complete(self):
        """
        Проверка завершения уровня путем сравнения уничтоженных и пропущенных врагов с общим количеством.

        Returns:
            bool: True, если уровень завершен, False в противном случае.
        """
        return (self.killed_enemies + self.missed_enemies) == len(self.enemy_list)

    def reset_level(self):
        """
        Сброс переменных, связанных с управлением врагами, для следующего уровня.
        """
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0

    def draw(self, surface):
        """
        Отрисовка фонового изображения карты на заданной поверхности.

        Args:
            surface (pygame.Surface): Поверхность, на которой нужно нарисовать карту.
        """
        surface.blit(self.image, (0, 0))
