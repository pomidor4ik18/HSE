import pygame as pg
from pygame.math import Vector2
import math
import constants as c
from enemy_data import ENEMY_DATA

class Enemy(pg.sprite.Sprite):
    """
    Класс Enemy представляет врага, который движется по пути, взаимодействует с миром и может быть уничтожен.
    """

    def __init__(self, enemy_type, waypoints, images):
        """
        Инициализация объекта врага.

        Args:
            enemy_type (str): Тип врага, определяющий его характеристики.
            waypoints (list): Список координат путевых точек.
            images (dict): Словарь изображений для различных типов врагов.
        """
        pg.sprite.Sprite.__init__(self)
        self.waypoints = waypoints
        self.pos = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.health = ENEMY_DATA.get(enemy_type)["health"]
        self.speed = ENEMY_DATA.get(enemy_type)["speed"]
        self.angle = 0
        self.original_image = images.get(enemy_type)
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self, world):
        """
        Обновление состояния врага: перемещение, поворот и проверка состояния здоровья.

        Args:
            world (World): Объект игрового мира.
        """
        self.move(world)
        self.rotate()
        self.check_alive(world)

    def move(self, world):
        """
        Перемещение врага по пути с учетом путевых точек и скорости.

        Args:
            world (World): Объект игрового мира.
        """
        # Определяем целевую путевую точку
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            # Враг достиг конца пути
            self.kill()
            world.health -= 1
            world.missed_enemies += 1

        # Рассчитываем расстояние до цели
        dist = self.movement.length()
        # Проверяем, больше ли оставшееся расстояние скорости врага
        if dist >= (self.speed * world.game_speed):
            self.pos += self.movement.normalize() * (self.speed * world.game_speed)
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

    def rotate(self):
        """
        Поворот врага в направлении следующей путевой точки.
        """
        # Рассчитываем расстояние до следующей точки
        dist = self.target - self.pos
        # Используем расстояние для вычисления угла
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
        # Поворачиваем изображение и обновляем прямоугольник
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def check_alive(self, world):
        """
        Проверка состояния здоровья врага и выполнение действий при его уничтожении.

        Args:
            world (World): Объект игрового мира.
        """
        if self.health <= 0:
            world.killed_enemies += 1
            world.money += c.KILL_REWARD
            self.kill()
