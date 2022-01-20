from random import choice, randint

import pygame
from creatures.enemy import Enemy
from math import sqrt
from objects.object import load_image, TRANSPARENT_OBJECTS, COLLIDE_OBJECTS
from items import functions as funcs
from items.items import Money

gravity = 0.35


class Warrior(Enemy):
    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):

        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)

    def loop(self, hero):
        self.count += 1
        if self.health > 0:
            radius = (self.rect.x - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2
            self.agro(radius)
            self.move(hero, radius)
            if self.agri and self.can_attack(radius):
                self.attack(hero)

    def attack_animation(self):
        pass

    def move(self, hero, radius):
        if not self.agri:
            super().move()
        else:
            radius = sqrt(radius)
            center = (self.rect.x + (self.size[-2] - radius * 2) // 2, self.rect.y + (self.size[-1] - radius * 2) // 2)
            self.line = funcs.Check_line(self.screen, radius, center, hero.rect.x, hero.rect.y, hero.image.get_width(),
                                         hero.image.get_height(), self)
            if self.line.check_direct():
                x, y = self.move_on_hero(hero)
                self.line.kill()
            else:
                self.find_direct(radius, self.rect.x, self.rect.y, hero)


class Zombie(Warrior):
    NAME = 'Зомби'
    image = load_image('zombie.png')
    frames_count = 9  # надо так как у всех разное
    death_list = ['zombie/die.png']

    def SPRITE_GROUP(self, new_group):
        self.set_cls_field(new_group)

    @classmethod
    def set_cls_field(cls, new_group):
        super().set_cls_field(new_group)
        Zombie.SPRITE_GROUP_ = pygame.sprite.Group()
        Zombie.SPRITE_GROUP_ = Enemy.SPRITE_GROUP_
        funcs.set_group_tiles(new_group)

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = Zombie.image
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.frames = self.make_animation_list(
            ['zombie/walk_up.png', 'zombie/walk_down.png', 'zombie/walk_left.png', 'zombie/walk_right.png'],
            self.frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Slime(Warrior):
    NAME = 'слизь'
    frames_count = 1
    image_list = [load_image('slime/slime2.png'), load_image('slime/slime3.png'), load_image('slime/slime3.png'),
                  load_image('slime/slime1.png')]
    death_list = ['goblin/die.png']

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = choice(Slime.image_list)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 1.5, self.image.get_height() * 1.5))

        self.death_frame = [[
            pygame.transform.scale(self.image, (self.image.get_width() - i * 4, self.image.get_height() - i * 4)) for i
            in range(5)], ]
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Wolf(Warrior):
    NAME = 'обратень'
    image = load_image('wolf/rest.png')
    frames_count = 9  # надо так как у всех разное
    death_list = ['wolf/die.png']

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = Wolf.image
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.frames = self.make_animation_list(
            ['wolf/walk_up.png', 'wolf/walk_down.png', 'wolf/walk_left.png', 'wolf/walk_right.png'], self.frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class IceWolf(Warrior):
    NAME = 'северный волк'
    image = load_image('ice_wolf/rest.png')
    frames_count = 9  # надо так как у всех разное
    death_list = ['ice_wolf/die.png']

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = Wolf.image
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.frames = self.make_animation_list(
            ['ice_wolf/walk_up.png', 'ice_wolf/walk_down.png', 'ice_wolf/walk_left.png', 'ice_wolf/walk_right.png'],
            self.frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Goblin(Warrior):
    NAME = 'Гоблин'
    image = load_image('goblin/rest.png')
    frames_count = 9  # надо так как у всех разное
    death_list = ['goblin/die.png']

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = Goblin.image
        self.money = 0
        self.death_frame = self.make_animation_list(self.death_list, 6)
        self.frames = self.make_animation_list(
            ['goblin/walk_up.png', 'goblin/walk_down.png', 'goblin/walk_left.png',
             'goblin/walk_right.png'], self.frames_count)
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)

    def stealing_money(self):
        if not self.money:
            s1 = funcs.quer('player\player.sql', F"""SELECT count,name from items where name like '%монет%'""")
            sum_ = 0
            for i in range(len(s1)):
                if s1[i][-1].startswith('мед'):
                    sum_ += s1[i][0]
                if s1[i][-1].startswith('сереб'):
                    sum_ += 100 * s1[i][0]
                if s1[i][-1].startswith('золот'):
                    sum_ += 10000 * s1[i][0]
            self.money = randint(0, int(sqrt(sum_)) + 1)
            self.damage_string[0] = F'у вас украли {self.money} монет'
            self.damage_string[1] = (self.rect.x - 25, self.rect.y - 10)
            self.damage_string[2] = self.count
            sum_ -= self.money
            b = sum_ % 100
            si = (sum_ % 10000) // 100
            g = sum_ // 10000
            for count, index, name in ((b, 8, 'медные монеты'), (si, 7, 'серебряные монеты'), (g, 6, 'золотые монеты')):
                if count:
                    s1 = funcs.quer('player\player.sql',
                                    f"""SELECT count from items where id = '{index}'""")
                    if not s1:
                        funcs.quer('player\player.sql',
                                   f"INSERT into items(id,count,name) VALUES('{index}','{0}','{name}')")
                    funcs.quer('player\player.sql',
                               f"UPDATE items SET count = '{count}' where id='{index}'")
            self.count = 0

    def loop(self, hero, kill=False):
        radius = (self.rect.x - hero.rect.x) ** 2 + (self.rect.y - hero.rect.y) ** 2
        self.agro(radius, 1.2)
        if self.money:
            if self.count >= 560:
                self.kill(True)
            elif self.count >= 380:
                self.open_portal()
            else:
                self.move_on_hero(hero, -1)
            self.draw(color_1='white', color_2='gold')
        else:
            if self.agri:
                self.move_on_hero(hero, 1)
                if self.can_attack(radius):
                    self.stealing_money()
            else:
                self.move(hero, radius)
            self.draw()

    def kill(self, die=False):
        if not die:
            Money(8, (self.rect.x, self.rect.y), 1, self.money)
        super().kill()

    def open_portal(self):
        color = pygame.Color(20 + self.count // 3, 0, 230 - self.count // 4)
        hsv_color = color.hsva
        color.hsva = (hsv_color[0], hsv_color[1], min(100, hsv_color[2] + 10), hsv_color[3])
        pygame.draw.ellipse(self.screen, color, (self.rect.x, self.rect.y - self.rect.height // 2,
                                                 self.rect.width, round(self.rect.height * 1.5)), 0)
        pygame.draw.ellipse(self.screen, pygame.Color(240, 240, 240), (self.rect.x, self.rect.y - self.rect.height // 2,
                                                                       self.rect.width, round(self.rect.height * 1.5)),
                            2)

    def take_damage(self, damage, pos=None, damage_type='обычный', check=True):
        self.count = min(self.count, 350)
        g = randint(0, min(3, self.money))
        if not pos:
            pos = self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2
        if g:
            Money(8, pos, 1, g)
            self.money -= g
        super().take_damage(damage, pos, damage_type, check)


class FARM_OBJECT(Enemy):
    def update(self, hero):
        if self.indark:
            self.image = load_image('dark_tile.png')
            self.image = pygame.transform.scale(self.image, (25, 25))
        else:
            self.image = load_image(self.imag)
        if self.health < 0:
            if hero:
                for i in range(randint(1, 6)):
                    self.stuff()
            self.kill()

    def take_damage(self, damage, pos, damage_type=None, check=False):
        if self.health < self.max_health * 0.8:
            self.image = load_image(f'{self.image1}')
        if self.health < self.max_health * 0.6:
            self.image = load_image(f'{self.image2}')
        if self.health < self.max_health * 0.4:
            self.image = load_image(f'{self.image3}')
        if self.health < self.max_health * 0.2:
            self.image = load_image(f'{self.image4}')
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        self.groups()[0].add(funcs.destroyedObject(f'{self.dest_object}', pos, randint(2, 5)))
        self.health -= damage * 2


class Rock(FARM_OBJECT):
    imag = 'rock_object.png'
    NAME = ''
    image1 = 'rock_object.png'
    image2 = 'rock_object.png'
    image3 = 'rock_object.png'
    image4 = 'rock_object.png'
    dest_object = 'items/rock.png'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = load_image(self.imag)
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Iron(FARM_OBJECT):
    imag = 'iron_ore_tile.png'
    NAME = ''
    image1 = 'iron_ore_tile.png'
    image2 = 'iron_ore_tile.png'
    image3 = 'iron_ore_tile.png'
    image4 = 'iron_ore_tile.png'
    dest_object = 'items/iron_ore.png'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = load_image(self.imag)
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Silver(FARM_OBJECT):
    imag = 'silver_ore_tile.png'
    NAME = ''
    image1 = 'silver_ore_tile.png'
    image2 = 'silver_ore_tile.png'
    image3 = 'silver_ore_tile.png'
    image4 = 'silver_ore_tile.png'
    dest_object = 'items/silver_ore.png'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = load_image(self.imag)
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Bronze(FARM_OBJECT):
    imag = 'copper_ore_tile.png'
    NAME = ''
    image1 = 'copper_ore_tile.png'
    image2 = 'copper_ore_tile.png'
    image3 = 'copper_ore_tile.png'
    image4 = 'copper_ore_tile.png'
    dest_object = 'items/copper_ore.png'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = load_image(self.imag)
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Charcoal(FARM_OBJECT):
    imag = 'charcoal_object.png'
    NAME = ''
    image1 = 'charcoal_object.png'
    image2 = 'charcoal_object.png'
    image3 = 'charcoal_object.png'
    image4 = 'charcoal_object.png'
    dest_object = 'items/charcoal.png'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = load_image(self.imag)
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Gold(FARM_OBJECT):
    imag = 'gold_ore_tile.png'
    NAME = ''
    image1 = 'gold_ore_tile.png'
    image2 = 'gold_ore_tile.png'
    image3 = 'gold_ore_tile.png'
    image4 = 'gold_ore_tile.png'
    dest_object = 'items/gold_ore.png'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = load_image(self.imag)
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)


class Tree(FARM_OBJECT):
    imag = 'tree_object.png'
    NAME = ''
    image1 = 'tree_object.png'
    image2 = 'tree_object.png'
    image3 = 'tree_object.png'
    image4 = 'tree_object.png'
    dest_object = 'items/rock.png'

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        self.image = load_image(self.imag)
        self.image = pygame.transform.scale(self.image, (25, 25))  # тут поменял!!!!
        super().__init__(screen, coords, health, armor, damage, damage_type, damage_resistance, speed,
                         speed_attack, len_attack, distance_of_vision_hero, hard_level, *group)
