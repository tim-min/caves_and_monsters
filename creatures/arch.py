import pygame
from creatures.enemy import Enemy
from objects.object import load_image, TRANSPARENT_OBJECTS, COLLIDE_OBJECTS
from items import functions as funcs
from pygame.math import Vector2
from math import atan2, degrees, radians, cos, sin


class Arch(Enemy):
    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)
        self.font = pygame.font.Font(None, 20)

    def move_(self, hero=None, radius=0, x=0, y=0, teleport=None):
        if not self.agri:
            super().move(x, y, teleport)
        else:
            if radius > self.len_attack ** 2:
                x, y = self.move_on_hero(hero, 1)
            elif radius < (self.len_attack ** 2) / 4:
                x, y = self.move_on_hero(hero, -1)

    def loop(self, hero):
        if self.health > 0:
            radius = (self.rect.x - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2
            self.agro(radius, 0.8)
            if not self.can_attack(radius):
                self.move_(hero, radius)
            else:
                self.attack_vector = self.attack_vector_finding(hero)

    def draw(self):
        super().draw()
        # pygame.draw.circle(self.screen, (255, 0, 0),
        #                    (self.rect.x + self.size[0] // 2, self.rect.y + self.size[1] // 2),
        #                    self.len_attack // 2, 1)


class Archer(Arch):
    image = load_image('archer/rest.png')
    NAME = 'скeлет лучник'
    frames_count = 9
    attack_frames_count = 13
    death_list = ['archer/die.png']

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = Archer.image
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.frames = self.make_animation_list(
            ['archer/walk_up.png', 'archer/walk_down.png', 'archer/walk_left.png', 'archer/walk_right.png'],
            self.frames_count)
        self.attack_frames = self.make_animation_list(['archer/attack_up.png', 'archer/attack_down.png',
                                                       'archer/attack_left.png', 'archer/attack_right.png'],
                                                      self.attack_frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)

    def attack(self, hero, check=False):
        if (self.rect.x - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2 <= self.len_attack ** 2:
            group = self.groups()[0]
            funcs.add_arrow((self.rect.x, self.rect.y), 'обычный',
                            self.damage * 2, (hero.rect.x, hero.rect.y), True, 360, group)
            self.last_attack = self.count
        else:
            return None


class SnowMag(Arch):
    NAME = 'ледяной маг'
    imag = load_image('ice_wizard/rest.png')
    frames_count = 9
    death_list = ['ice_wizard/die.png']
    attack_frames_count = 7

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = SnowMag.imag
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.attack_frames = self.make_animation_list(['ice_wizard/attack_up.png', 'ice_wizard/attack_down.png',
                                                       'ice_wizard/attack_left.png', 'ice_wizard/attack_right.png'],
                                                      self.attack_frames_count)
        self.frames = self.make_animation_list(
            ['ice_wizard/walk_up.png', 'ice_wizard/walk_down.png', 'ice_wizard/walk_left.png',
             'ice_wizard/walk_right.png'],
            self.frames_count)
        self.bullet = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        self.bullet_size = 10
        self.v = (0, 0)

        pygame.draw.circle(self.bullet, pygame.Color('ghostwhite'),
                           (self.bullet.get_width() // 2,
                            self.bullet.get_height() // 2), self.bullet.get_height() // 2)
        self.big_bull = pygame.transform.scale2x(pygame.transform.scale2x(self.bullet))
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)

    def attack(self, hero, check=False):
        v = (self.v[0] / 20, self.v[1] / 20)
        self.groups()[0].add(funcs.Fire((self.rect.x, self.rect.y), 'cold', self.damage, self.big_bull, v=v,
                                        attack=True))
        self.bullet_size = self.bullet.get_width()

    def attack_animation(self, hero):
        super().attack_animation(hero)
        hero_v = Vector2(hero.rect.x, hero.rect.y)
        my_v = Vector2(self.rect.x, self.rect.y)
        self.v = hero_v - my_v
        vx = 1 if self.v[0] > 0 else -1
        vy = 1 if self.v[1] > 0 else -1
        self.bullet_size *= 1.15
        x = self.rect.x + vx * (self.bullet_size - self.bullet.get_width()) // 2
        y = self.rect.y + vy * (self.bullet_size - self.bullet.get_height()) // 2
        self.screen.blit(pygame.transform.scale(
            self.bullet,
            (self.bullet_size, self.bullet_size)),
            (x, y))

