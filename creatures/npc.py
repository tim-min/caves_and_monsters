from random import choice

import pygame

from creatures.enemy import Enemy
from math import sqrt, cos, atan2, degrees, sin
from objects.object import load_image, TRANSPARENT_OBJECTS, COLLIDE_OBJECTS


class NPC(Enemy):
    IMAGE = 'zombie.png'
    NAME = ''
    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group, radius=100):
        self.image = load_image(NPC.IMAGE)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)
        self.s_x, self.s_y = coords
        self.radius = radius
        self.vx, self.vy = choice([1, 1.4, -1.4, -1]), choice([0.6, 1.2, 1, -0.6, -1, -1.2])

    def update(self, hero=None, kill=False):
            self.draw_()
            self.npc_move()

    def npc_move(self):
        if self.s_x - self.rect.x > self.radius:
            self.vx = choice([0.7, 0.9, 1.1, 0.8, 0.6, 0.5, 1])
        if self.rect.x - self.s_x > self.radius:
            self.vx = -choice([0.7, 0.9, 1.1, 0.8, 0.6, 0.5, 1])
        if self.s_y - self.rect.y > self.radius:
            self.vy = choice([0.7, 0.9, 1.1, 0.8, 0.6, 0.5, 1])
        if self.rect.y - self.s_y > self.radius:
            self.vy = -choice([0.7, 0.9, 1.1, 0.8, 0.6, 0.5, 1])
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw_(self):
        # pygame.draw.circle(self.screen, (255, 255, 255),
        #                    (self.s_x + self.size[-2] // 2, self.s_y + self.size[-1] // 2), self.radius, 1)
        pass
