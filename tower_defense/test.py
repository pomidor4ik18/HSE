import pytest
import pygame as pg
from pygame.math import Vector2
from main import Enemy, World
import constant as c
from enemy_data import ENEMY_DATA
import json

@pytest.fixture(scope="module")
def setup_pygame():
    pg.init()
    pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    yield
    pg.quit()


@pytest.fixture
def setup_world(setup_pygame):
    with open('levels/level.tmj') as file:
        world_data = json.load(file)
    map_image = pg.image.load('levels/level.png').convert_alpha()
    world = World(world_data, map_image)
    world.process_data()
    world.process_enemies()
    return world


@pytest.fixture
def setup_enemy_images():
    enemy_images = {
        "weak": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
        "medium": pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
        "strong": pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
        "elite": pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
    }
    return enemy_images


@pytest.fixture
def setup_enemy(setup_pygame, setup_enemy_images):
    waypoints = [(0, 0), (100, 0)]
    enemy_type = "weak"
    enemy = Enemy(enemy_type, waypoints, setup_enemy_images)
    return enemy


def test_enemy_initialization(setup_enemy):
    enemy = setup_enemy
    assert enemy.health == ENEMY_DATA["weak"]["health"]
    assert enemy.speed == ENEMY_DATA["weak"]["speed"]
    assert enemy.pos == Vector2(0, 0)
    assert enemy.target_waypoint == 1


def test_enemy_move(setup_enemy, setup_world):
    enemy = setup_enemy
    world = setup_world
    initial_pos = enemy.pos.copy()

    enemy.move(world)

    assert enemy.pos != initial_pos
    assert enemy.pos.x > initial_pos.x  # Враг должен двигаться вправо


def test_enemy_reach_end(setup_enemy, setup_world):
    enemy = setup_enemy
    world = setup_world
    enemy.target_waypoint = len(enemy.waypoints)  # Симулируем достижение конца пути

    initial_health = world.health
    initial_missed = world.missed_enemies

    enemy.move(world)

    assert not enemy.alive()
    assert world.health == initial_health - 1
    assert world.missed_enemies == initial_missed + 1


def test_enemy_rotate(setup_enemy):
    enemy = setup_enemy
    enemy.target = Vector2(100, 0)

    enemy.rotate()

    assert enemy.angle == 0  # Враг должен смотреть вправо


def test_enemy_check_alive(setup_enemy, setup_world):
    enemy = setup_enemy
    world = setup_world

    enemy.health = 0
    initial_killed = world.killed_enemies
    initial_money = world.money

    enemy.check_alive(world)

    assert not enemy.alive()
    assert world.killed_enemies == initial_killed + 1
    assert world.money == initial_money + c.KILL_REWARD
