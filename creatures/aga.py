from math import cos, sin, radians
from random import randint, choice

from creatures import enemy
import pygame
from objects.object import load_image
from items import functions as funcs


class BOS_1(enemy.Enemy):
    image = load_image('boss_1/rest.png')
    frames_count = 9
    death_list = ['boss_1/die.png']
    NAME = 'ЗИК'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = BOS_1.image
        self.frames = self.make_animation_list(
            ['boss_1/move_up.png', 'boss_1/move_down.png', 'boss_1/move_left.png', 'boss_1/move_right.png'],
            self.frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.rect.x = 900
        self.rect.y = 450
        self.phases = (1, 2)
        self.phase = 1

        self.ord_vector = [(900, 450), (1200, 250), (1200, 650), (900, 450), (600, 250), (600, 650)]
        self.g = 0
        self.x = self.rect.x
        self.y = self.rect.y
        self.attack_frames_count = 7
        self.attack_frames = self.make_animation_list(['boss_1/throw.png'], 7)

    def loop(self, hero):
        # for i in self.ord_vector:  # синие кружочки убрать в последней версии
        #     pygame.draw.circle(self.screen, pygame.Color('blue'), i, 10)
        if self.phase == 1:
            self.ordinary()
            if self.health < self.max_health * 0.4:
                self.phase = 2
                self.damage *= 2
        else:
            self.extraordinary(hero)
        radius = (self.rect.x - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2
        if self.can_attack(radius):
            self.attack(hero)

    def ordinary(self):
        if not self.count % 200:
            self.attack_animation_now = self.attack_frames_count - 2
            self.g = (self.g + 1) % 6
        else:
            self.ord_move()

    def extraordinary(self, hero):
        self.move_on_hero(hero)
        self.extraordinary_attack(hero)

    def ordinary_attack(self, n=5, time=100):
        group = self.groups()
        group[0].add(funcs.rock(self.screen, (self.rect.x, self.rect.y), n, time))

    def attack_animation(self, hero):

        self.image_now = self.attack_frames[0][self.attack_frames_count - self.attack_animation_now - 2]
        self.attack_animation_now -= 1
        if self.attack_animation_now == -1:
            if self.phase == 1:
                self.ordinary_attack(10)

    def extraordinary_attack(self, hero):
        if not self.count % 150:
            self.ordinary_attack(4, 40)
        if not self.count % 300:
            group = self.groups()
            group[0].add(funcs.circle_attack((self.rect.x, self.rect.y), 150))
        if not self.count % 90:
            group = self.groups()
            group[0].add(
                funcs.circle_attack((hero.rect.x + randint(-100, 100),
                                     hero.rect.y + randint(-100, 100)), 60))

    def ord_move(self):
        new_g = (self.g + 1) % 6
        self.x += (self.ord_vector[new_g][0] - self.ord_vector[self.g][0]) / 200
        self.rect.x = round(self.x)
        self.y += (self.ord_vector[new_g][1] - self.ord_vector[self.g][1]) / 200
        self.rect.y = round(self.y)
        self.anim((self.ord_vector[new_g][0] - self.ord_vector[self.g][0]) / 200, (self.ord_vector[new_g][1] -
                                                                                   self.ord_vector[self.g][1]) / 200)


class BOS_2(enemy.Enemy):
    image = load_image('boss_2/rest.png')
    frames_count = 9
    death_list = ['boss_2/die.png']
    NAME = 'Айрон'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = BOS_2.image
        self.frames = self.make_animation_list(
            ['boss_2/walk_up.png', 'boss_2/walk_down.png','boss_2/move_left.png', 'boss_2/move_right.png'],
            self.frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.rect.x = 900
        self.rect.y = 450
        self.phases = (1, 2)
        self.phase = 1
        self.check_pos = (600, 1200)
        self.v = 2
        self.group = []
        self.attack_frames_count = 6
        self.attack_frames = self.make_animation_list(['boss_2/attack_up.png', 'boss_2/attack_down.png',
                                                       'boss_2/attack_left.png', 'boss_2/attack_right.png'],
                                                      self.attack_frames_count)
        self.now_attack = []

    def loop(self, hero):
        if self.phase == 1:
            if self.health < 0.5 * self.max_health:
                self.phase = 2
            self.ordinary(hero)
        else:
            self.extraordinary(hero)

    def ordinary(self, hero):
        if self.rect.x > max(self.check_pos):
            self.v = -1
        elif self.rect.x < min(self.check_pos):
            self.v = 1
        self.anim(self.v, 0)
        self.rect.x += self.v
        group = self.groups()[0]

        for i in filter(lambda x: isinstance(x, funcs.pair_ball), group):
            if len(i.s1) > 3:
                pygame.draw.aalines(self.screen, pygame.Color('cyan2'), False, i.s1)
        if not self.count % 200:
            self.now_attack.append(self.attck_1)
            self.attack_vector = self.attack_vector_finding(hero)
        elif not all(self.count % i for i in (70, 90, 110)):
            self.now_attack.append(self.attack_2)
            self.attack_vector = self.attack_vector_finding(hero)
        elif not self.count % 150:
            self.now_attack.append(self.attack_3)
            self.attack_vector = self.attack_vector_finding(hero)

    def attck_1(self, group, hero):
        surf = funcs.snow_surf()
        group.add(funcs.pair_ball((self.rect.x, self.rect.y), 'cold', 10, surf,
                                  attack=True, cos_=True,
                                  circle=False, cicrle_times=[(i - 80, i) for i in range(160, 1200, 160)]))
        group.add(funcs.pair_ball((self.rect.x, self.rect.y), 'cold', 20, surf,
                                  attack=True, cos_=False,
                                  circle=False, cicrle_times=[(i - 80, i) for i in range(120, 1200, 160)]))

    def attack_2(self, group, hero):
        surf = pygame.Surface((8, 2), pygame.SRCALPHA, 32)
        surf.fill(pygame.Color('cyan2'))
        surf = pygame.transform.rotate(
            surf,
            180 - (pygame.math.Vector2((hero.rect.x, hero.rect.y)) -
                   pygame.math.Vector2(self.rect.x, self.rect.y)).as_polar()[1])
        group.add(funcs.Fire((self.rect.x, self.rect.y), 'cold', 5, surf, True))

    def attack_3(self, group, hero):
        x, y = (hero.rect.x + randint(-70, 70), hero.rect.y + randint(-70, 70))
        group.add(funcs.line1((x, y),
                              'cold', 0.5, color='cyan2', v=1))
        group.add(funcs.line1((x, y),
                              'cold', 0.5, color='cyan2', v=-1))

    def attack_5(self, group, hero):
        group.add(funcs.mega_snow_boll((self.rect.x, self.rect.y), 'cold', 50, funcs.snow_surf(25),
                                       attack=True, death_time=150, destroy=15))

    def extraordinary(self, hero):
        self.image = self.rest_image
        group = self.groups()[0]
        if not self.count % 200:
            surf = pygame.Surface((5, 5), pygame.SRCALPHA, 32)
            pygame.draw.aalines(surf, pygame.Color('cyan2'), True, ((0, 0), (surf.get_width(), 0),
                                                                         (surf.get_width() // 2, surf.get_height())), 2)
            self.group.append(funcs.ships((self.rect.x, self.rect.y), self.damage, 'cold', surf, 4,
                                          s_angle=len(self.group) * 30))
            group.add(self.group[-1])
        if self.group:
            for i in range(len(self.group)):
                if self.group[i]:
                    self.group[i].loop()
                    for j in self.group[i]:
                        if j not in group:
                            group.add(j)
                else:
                    self.group[i] = 0
        else:
            if self.rect.x > max(self.check_pos):
                self.v = -1
            elif self.rect.x < min(self.check_pos):
                self.v = 1
            self.rect.x += self.v
        if not self.count % 300:
            self.now_attack.append(self.attack_5)
            self.attack_vector = self.attack_vector_finding(hero)

    def attack(self, hero, check=None):
        if not self.now_attack:
            pass
        else:
            group = self.groups()[0]
            self.now_attack.pop(0)(group, hero)


class BOS_3(enemy.Enemy):
    image = load_image('boss_3/rest.png')
    frames_count = 9
    death_list = ['boss_3/die.png']
    NAME = 'ТИМУР БОТ'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = BOS_3.image
        self.frames = self.make_animation_list(
            ['boss_3/walk_up.png', 'boss_3/walk_down.png', 'boss_3/walk_left.png', 'boss_3/walk_right.png'],
            self.frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.rect.x = 900
        self.rect.y = 450
        self.phases = (1, 2)
        self.phase = 1
        self.check_pos = [(self.rect.x + 300 * cos(radians(i * 144)),
                           self.rect.y + 300 * sin(radians(i * 144))) for i in range(15)]
        self.g = 0
        self.v = 2
        self.x, self.y = self.rect.x, self.rect.y = self.check_pos[0]
        self.now = 0
        self.last = 120
        self.anydazx = 0

    def ord_move(self):
        new_g = (self.g + 1) % len(self.check_pos)
        self.x += (self.check_pos[new_g][0] - self.check_pos[self.g][0]) / 200
        self.rect.x = round(self.x)
        self.y += (self.check_pos[new_g][1] - self.check_pos[self.g][1]) / 200
        self.rect.y = round(self.y)
        self.anim((self.check_pos[new_g][0] - self.check_pos[self.g][0])/ 200,(self.check_pos[new_g][1] -
                  self.check_pos[self.g][1]) / 200)

    def loop(self, hero):
        # for i in self.check_pos:
        #     pygame.draw.circle(self.screen, pygame.Color('blue'), i, 10)
        if self.phase == 1:
            self.ordinary(hero)
            if self.health < self.max_health * 0.4:
                self.phase = 2
                self.damage *= 2
        else:
            self.extraordinary(hero)
        radius = (self.rect.x - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2
        if self.can_attack(radius):
            self.attack(hero)

    def ordinary(self, hero):
        group = self.groups()[0]
        group.add(funcs.circle_attack((self.rect.x + 15, self.rect.y + 20), 30, 'cyan2',
                                      1))
        self.ord_move()
        if not self.count % 200:
            self.g = (1 + self.g) % len(self.check_pos)
            surf = funcs.electric_surf(7)
            group.add(funcs.Turel((hero.rect.x + randint(-70, 70), hero.rect.y + randint(-70, 70)), 'electric', surf,
                                  self.damage, 100,
                                  'cyan2'))

        if not self.count % 40:
            group.add(funcs.Molny((self.rect.x, self.rect.y), 'electric', self.damage, None, True, 1000, 0,
                                  (hero.rect.x, hero.rect.y)))

    def extraordinary(self, hero):
        group = self.groups()[0]
        if self.now == self.last or not self.now:
            self.anydazx = (self.anydazx + 1) % 2
        if self.anydazx:
            self.now += 1
        else:
            self.now -= 1
        group.add(funcs.circle_attack((self.rect.x + 15, self.rect.y + 20), self.now, 'coral', death_time=1))
        if not self.count % 60:
            group.add(funcs.pair_ball((self.rect.x + 15, self.rect.y + 20), 'electric', self.damage * 2,
                                      funcs.electric_surf(), True, 600, 3, randint(0, 2), False, True, [(0, 600)],
                                      amp=self.last * 2 - self.now))
        if not self.count % 170:
            ball = funcs.mega_snow_boll((self.rect.x + 15, self.rect.y + 20), 'electric', self.damage * 15,
                                        funcs.electric_surf(28), True, 150, 15)
            ball.change_set(funcs.electric_surf(), 'electric', 5, 0, 72)
            group.add(ball)
