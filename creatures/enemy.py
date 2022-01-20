from random import choice, randint
import pygame
from objects.object import load_image, TRANSPARENT_OBJECTS, COLLIDE_OBJECTS
from items.items import Items
from items import functions as funcs

TRANSPARENT_OBJECTS_ = list(map(int, TRANSPARENT_OBJECTS))
DAMAGES = {'potion': 1.1, 'fire': 1.3, 'обычный': 1, 'cold': 1.2, 'electric': 1.4}


def make_a_free_point(map_, screen):
    x_pos, y_pos = screen.get_width() / 2 - 41 * 25 / 2, screen.get_height() / 2 - 36 * 25 / 2
    with open(map_, "r") as file:
        room_map = list(map(lambda x: list(map(int, x.split())), file.readlines()))
    list_free_point = {}
    for x in range(len(room_map)):
        for obj in range(len(room_map[x])):
            if room_map[x][obj] in COLLIDE_OBJECTS:
                os_y = [0, 0]
                os_x = [0, 0]
                if 0 < x < len(room_map) - 1 and 0 < obj < len(room_map[x]) - 1:
                    if room_map[x - 1][obj] in COLLIDE_OBJECTS:
                        os_y[0] = 1
                    if room_map[x + 1][obj] in COLLIDE_OBJECTS:
                        os_y[1] = 1
                    if sum(os_y) < 2:
                        if room_map[x][obj - 1] in COLLIDE_OBJECTS:
                            os_x[0] = 1
                        if room_map[x][obj + 1] in COLLIDE_OBJECTS:
                            os_x[1] = 1
                        if sum(os_y) + sum(os_x) == 2:
                            x_h = x_pos
                            y_h = y_pos
                            if os_x[0]:
                                x_h = x_h + 27
                            else:
                                x_h = x_h - 2
                            if os_y[0]:
                                y_h = y_h + 27
                            else:
                                y_h = y_h - 2
                            list_free_point.add((x_h, y_h))
                        elif sum(os_y) + sum(os_x) == 1:
                            if os_y[0]:
                                list_free_point.add((x_pos - 2, y_pos + 27))
                                list_free_point.add((x_pos + 27, y_pos + 27))
                            elif os_y[1]:
                                list_free_point.add((x_pos - 2, y_pos - 2))
                                list_free_point.add((x_pos + 27, y_pos - 2))
                            elif os_x[0]:
                                list_free_point.add((x_pos + 27, y_pos - 2))
                                list_free_point.add((x_pos + 27, y_pos + 27))
                            else:
                                list_free_point.add((x_pos - 2, y_pos - 2))
                                list_free_point.add((x_pos - 2, y_pos + 27))
                        elif not sum(os_y) + sum(os_x):
                            list_free_point.add((x_pos - 2, y_pos - 2))
                            list_free_point.add((x_pos + 27, y_pos - 2))
                            list_free_point.add((x_pos - 2, y_pos + 27))
                            list_free_point.add((x_pos + 27, y_pos + 27))


class Enemy(pygame.sprite.Sprite):
    SPRITE_GROUP_ = pygame.sprite.Group()
    SPRITE_CHECK = pygame.sprite.Group()
    SPRITE_ENEMY = pygame.sprite.Group()
    FREEPOINT = []
    NAME = ''

    def __init__(self, screen, coords, health, armor, damage, damage_type, damage_resistance: dict, speed,
                 speed_attack, len_attack, distance_of_vision_hero, hard_level, *group):
        super().__init__(*group)
        self.rest_image = self.image
        self.screen = screen  # экран
        self.health = health  # хп
        self.size = self.image.get_rect()[2:]  # размеры моба
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[-1])  # его квадрат
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.old_rect_x = self.rect.x
        self.old_rect_y = self.rect.x  # координаты для проверки хода ------------ НУЖНЫ!!!!!
        self.armor = armor
        self.s_speed = speed
        self.s_speed_attack = speed_attack
        self.damage = damage
        self.damage_type = damage_type
        self.damage_resistance = damage_resistance
        self.speed = speed
        self.count = 0
        self.max_health = health
        self.last_attack = 0
        self.mask = pygame.mask.from_surface(self.image)  # для норм колизии
        self.my_cache = {}
        self.agri = False
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        self.damage_string = ["", (None, None), 0]
        self.current_animation = 0
        self.current_frame = 0
        self.speed_attack = speed_attack
        self.len_attack = len_attack
        self.distance_of_vision_Hero = distance_of_vision_hero
        self.line = None
        self.hard_level = hard_level
        self.time_damages = []
        self.cold_time = 0
        self.attack_animation_now = -1
        self.attack_vector = 0
        self.death_time = 0
        self.indark = False
        self.image_now = self.image
        Enemy.SPRITE_ENEMY.add(self)

    def todark(self, vis):
        self.indark = not vis

    def attack_vector_finding(self, hero):
        if abs(hero.rect.x - self.rect.x) > abs(hero.rect.y - self.rect.y):
            if hero.rect.x < self.rect.x:
                g = 2
            else:
                g = 3
        else:
            if hero.rect.y < self.rect.y:
                g = 0
            else:
                g = 1
        self.attack_animation_now = self.attack_frames_count - 2
        return g

    def cut_sheet(self, sheet, columns, rows, n):
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        result = list()
        x_pos = 0
        for i in range(columns - 1):
            result.append(sheet.subsurface(pygame.Rect(
                (x_pos, 0), rect.size)))
            # ------------------------------ тут я изменил!!!!! --------------------------
            x_pos += n  # n теперь это размер кадра по x + отступ между кадрами
            # ------------------------------- тут я изменил!!!! --------------------------
        return result

    def attack_animation(self, hero):
        self.image_now = self.attack_frames[self.attack_vector][self.attack_frames_count - self.attack_animation_now
                                                                - 2]
        self.attack_animation_now -= 1
        if self.attack_animation_now == -1:
            self.attack(hero)

    def class_type(self):
        return str(type(self)).split('.')[-1][:-2]

    def stuff(self):
        indexes = dict_mobs[self.class_type()]['id']
        if indexes[0]:
            indexes = Items.get_random_item(Items, tuple(indexes))
            for index in indexes:
                index[-1](index[0], (self.rect.x + randint(-20, 20), self.rect.y + randint(-20, 20)),
                          self.hard_level)

    def make_animation_list(self, s1, frames_count, n=63.8):
        frames = [self.cut_sheet(load_image(s1[i]), frames_count, 1, n) for i in range(len(s1))]
        return frames

    @classmethod
    def set_FREEPOINT(cls, freepoint):
        Enemy.FREEPOINT = list(freepoint)

    @classmethod
    def set_cls_field(cls, new_group):
        s1 = list(filter(lambda x: x.id in COLLIDE_OBJECTS, [i for i in new_group]))
        Enemy.SPRITE_GROUP_ = pygame.sprite.Group()
        for i in s1:
            Enemy.SPRITE_GROUP_.add(i)
        return Enemy.SPRITE_GROUP_

    def move(self, hero=None, x=0, y=0, teleport=False):
        s1 = [choice((0, 1)) for j in range(100)]
        if (self.rect.x, self.rect.y) != (self.old_rect_x, self.old_rect_y):
            if sum(s1) < 60:
                if not x:
                    x = (self.rect.x - self.old_rect_x) * self.speed
                if not y:
                    y = (self.rect.y - self.old_rect_y) * self.speed
            else:
                if sum(s1) < 62:
                    if not y:
                        y = -(self.rect.y - self.old_rect_y) * self.speed
                        x = self.rect.x - self.old_rect_x + self.speed
                else:
                    if not x:
                        x = -(self.rect.x - self.old_rect_x) * self.speed
                        y = self.rect.y - self.old_rect_y + self.speed
        else:
            if not x:
                x = choice([-3, -2, 2, 3])
            if not y:
                y = choice([-3, -2, 2, 3])
        if not teleport:
            if abs(x) > self.speed:
                x = self.speed * abs(x) // x
            if abs(y) > self.speed:
                y = self.speed * abs(y) // y

        self.old_rect_x = self.rect.x
        self.old_rect_y = self.rect.y
        x = - x if self.rect.x + x < self.size[0] or self.rect.x + x > self.screen.get_width() - \
                   self.size[0] else x
        y = - y if self.rect.y + y < self.size[1] or self.rect.y + y > self.screen.get_height() - \
                   self.size[0] else y
        self.check_move(x, y)
        self.anim(x, y)
        return x, y

    def anim(self, vx, vy):
        if self.frames_count > 1:
            if vy < 0:
                self.current_animation = 0
            if vy > 0:
                self.current_animation = 1
            if vx < 0:
                self.current_animation = 2
            if vx > 0:
                self.current_animation = 3
            if vx == 0 and vy == 0:
                self.current_animation = -1
            if not self.count % 2:
                if self.current_animation > -1:
                    self.image_now = self.frames[self.current_animation][
                        self.current_frame]  # меняем image по анимации и фрэйму
                    if self.current_frame < len(
                            self.frames[self.current_animation]) - 1:  # если сейчас не последний фрэйм, то прибавляем
                        self.current_frame += 1
                    else:
                        self.current_frame = 0  # если последний, то ставим на первый
                else:
                    self.image_now = self.rest_image

    def can_move(self, *args):
        args = list(args) + [self]
        g = []
        for sprite in Enemy.SPRITE_GROUP_:
            if pygame.sprite.collide_mask(self, sprite):
                g.append(sprite)
        if len(g):
            return False
        return True

    def check_move(self, x, y):
        self.rect.move(x, y)
        if self.can_move():
            self.rect.x += round(x)
            self.rect.y += round(y)
        else:
            self.rect.x -= x
            self.rect.y -= y

    def move_on_hero(self, hero, k=1):
        x, y = 0, 0
        if hero.rect.x >= self.rect.x:
            x = self.speed * k
        elif hero.rect.x < self.rect.x:
            x = -self.speed * k
        if hero.rect.y >= self.rect.y:
            y = self.speed * k
        elif hero.rect.y < self.rect.y:
            y = -self.speed * k
        self.check_move(x, y)
        self.anim(x, y)
        return min((self.speed * x) // abs(x), x), min(self.speed * y // abs(y), y)

    def draw(self, color_1='white', color_2='red'):
        # pygame.draw.circle(self.screen, (255, 255, 255),
        #                    (self.rect.x + self.size[-2] // 2, self.rect.y + self.size[-1] // 2), self.len_attack, 1)
        pygame.draw.rect(self.screen, pygame.Color(color_1), [self.rect.x, self.rect.y - 20, 50, 10])
        pygame.draw.rect(self.screen, pygame.Color(color_2),
                         [self.rect.x, self.rect.y - 20, 50 * self.health // self.max_health, 10])
        text = self.font.render(self.NAME, True, pygame.Color('white'))
        self.screen.blit(text, (self.rect.x + (self.rect.width - text.get_width()) // 2, self.rect.y - 40))
        if self.damage_string[0]:
            text = self.font.render(self.damage_string[0], True, pygame.Color('red'))
            self.screen.blit(text, self.damage_string[1])
            if self.damage_string[-1] < self.count - 120:
                self.damage_string = ['', (0, 0), 0]
        for j in self.time_damages:
            for i in j[-1]:
                self.screen.blit(i[0], (self.rect.x + i[1][0] + randint(i[2][0], i[2][1]),
                                        self.rect.y + i[1][1] + randint(i[3][0], i[3][1])))

    def agro(self, radius, k=1):  # агриться если герой в радиусе видимости
        if radius <= self.distance_of_vision_Hero ** 2:
            self.agri = True
            self.speed = self.s_speed * k
        else:
            if self.agri and radius >= self.distance_of_vision_Hero ** 2 * 1.5:
                self.agri = False
                self.speed = self.s_speed

    def attack(self, hero, check=False):
        new_dam = randint(0, self.damage)
        if check:
            return 1
        if new_dam >= hero.armor:
            self.last_attack = self.count
            damage = randint(1, self.damage)
            hero.take_damage(self.damage,self.damage_type)
            self.damage_string[0] = f'-{damage}'
            self.damage_string[1] = hero.pos[0], hero.pos[1] - 10
            self.damage_string[-1] = self.count
        else:
            return None

    def take_damage(self, damage, pos=None, damage_type='electric', check=True):
        damage = damage * DAMAGES[damage_type]
        if check and damage_type in self.damage_resistance.keys():
            damage *= self.damage_resistance[damage_type]
        if damage_type == 'potion':
            self.take_potion_damage(damage)
        elif damage_type == 'fire':
            self.take_fire_damage(damage)
        elif damage_type == 'cold':
            self.take_cold_damage(damage)
        elif damage_type == 'electric':
            self.take_electric_damage(damage)
        else:
            self.health -= damage

    def take_electric_damage(self, damage, time=120):
        self.health -= damage / 4
        s1 = []
        for i in range(randint(2, 6)):
            x, y = randint(0, self.rect.width // 3), randint(
                self.rect.height // 10, int(self.rect.height * 0.6))
            surf = pygame.Surface((15, 15), pygame.SRCALPHA, 32)
            pygame.draw.line(surf, pygame.Color('white'), (0, 0), (randint(6, 15), randint(6, 15)), 2)

            surf = pygame.transform.rotate(surf, randint(0, 360))
            s1.append((surf, (x, y), (10, 10), (-10, 10)))
        self.time_damages.append((time, damage * 3 / 4 / time, s1))

    def can_attack(self, radius):
        if not self.last_attack or self.count - 60 / self.speed_attack > self.last_attack:
            if radius <= self.len_attack ** 2:
                return True
        return False

    def take_potion_damage(self, damage, time=360):
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA, 32)
        surf.set_alpha(40)
        pygame.draw.ellipse(surf, pygame.Color("green"),
                            (0, 0, self.rect.width, self.rect.height))
        self.time_damages.append((time, damage / time, [(surf, (0, 0), (0, 0), (0, 0))]))

    def take_fire_damage(self, damage, time=360):
        self.health -= damage / 2
        s1 = []
        for i in range(randint(2, 6)):
            x, y = randint(self.rect.width // 10, int(self.rect.width * 0.9)), randint(
                self.rect.height // 10, int(self.rect.height * 0.9))
            surf = pygame.Surface((6, 6))
            pygame.draw.rect(surf, pygame.Color('yellow'), (0, 4, 6, 3))
            pygame.draw.rect(surf, pygame.Color('red'), (0, 0, 6, 4))
            s1.append((surf, (x, y), (-5, 5), (-4, 4)))
        self.time_damages.append((time, damage / 2 / time, s1))

    def take_cold_damage(self, damage, time=360):
        self.health -= damage
        g, time = (1, time) if 'cold' not in self.damage_resistance.keys() \
            else (self.damage_resistance['cold'], time / self.damage_resistance['cold'])
        self.speed_attack /= (1.3 / g)
        self.speed /= (1.3 / g)
        self.cold_time = time
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA, 32)
        surf.set_alpha(35)
        pygame.draw.ellipse(surf, pygame.Color("blue"), (0, 0, self.rect.width, self.rect.height))
        self.time_damages.append((time, 0, [(surf, (0, 0), (0, 0), (0, 0))]))

    def find_direction(self, radius, x, y, hero, su=0):
        if (x, y) in self.my_cache.keys():
            if self.my_cache[(x, y)]:
                return self.my_cache[(x, y)]
            else:
                self.my_cache[(x, y)].append((x, y))
        if funcs.Check_line(self.screen, radius, (x, y), hero.rect.x, hero.rect.y, hero.image.get_width(),
                            hero.image.get_height()).check_direct():
            return x, y
        my_free_point = sorted(Enemy.FREEPOINT, key=lambda i: (i[0] - x) ** 2 + (i[1] - y) ** 2)
        if (x, y) in my_free_point:
            del my_free_point[my_free_point.index((x, y))]
        for i in my_free_point:
            if i in self.my_cache or funcs.Check_line(self.screen, radius, (x, y), i[0], i[1], 0, 0).check_direct():
                del my_free_point[my_free_point.index(i)]
        my_free_point = my_free_point[:3]
        for i in range(len(my_free_point)):
            self.find_direction(radius, my_free_point[i][0], my_free_point[i][1], hero, su + i)
        return my_free_point[0]

    def find_direct(self, radius, x, y, hero):
        # self.my_cache = {}
        # for i in Enemy.FREEPOINT:
        #     self.my_cache[i] = []
        # self.find_direction(radius, x, y, hero)
        # print(*list([(key, item) for key, item in self.my_cache.items() if item]), sep='  ')
        return None
        # self.my_cache.clear()

    def death_animation(self):

        if self.death_time < self.count - 25:
            self.image_now = self.death_frame[0][4]
        elif self.death_time < self.count - 20:
            self.image_now = self.death_frame[0][3]
        elif self.death_time < self.count - 15:
            self.image_now = self.death_frame[0][2]
        elif self.death_time < self.count - 10:
            self.image_now = self.death_frame[0][1]
        elif self.death_time < self.count - 5:
            self.image_now = self.death_frame[0][0]

    def update(self, hero, check=False, kill=False):
        self.count += 1

        if not self.death_time:
            if kill:
                self.kill()
                self.health = 0
            sadzxc = 0
            for i in range(len(self.time_damages)):
                i -= sadzxc
                if self.time_damages[i][0]:  # наносит урон если есть яд и тд
                    self.health -= self.time_damages[i][1]
                    self.time_damages[i] = (self.time_damages[i][0] - 1, *self.time_damages[i][1:])
                else:
                    del self.time_damages[i]
                    sadzxc += 1
            if self.cold_time:
                self.speed = self.s_speed * 0.8
            if not hero:
                raise ValueError("не был передан игрок")
            if self.attack_animation_now != -1:  # если сейчас происходит анимация атаки то анимация
                if self.count % 2:
                    self.draw()
                    self.attack_animation(hero)
            else:
                if self.health > 0:  # если хп больше нуля то update у самого класса
                    self.loop(hero)
                    if not self.indark:
                        self.draw()
                else:
                    self.stuff()
                    self.death_time = self.count
        else:
            self.death_animation()
            if self.count > self.death_time + 120:
                self.kill()
        if self.indark:
            self.image = load_image('dark_tile.png')
        else:
            self.image = self.image_now


from creatures.warrior import Zombie, Slime, Wolf, Rock, Goblin, Charcoal, IceWolf, Iron, Gold, Bronze, Silver
from creatures.arch import Archer, SnowMag
from creatures.npc import NPC
from creatures.aga import BOS_1, BOS_2, BOS_3


def create_mob(screen, coords, level, s1, *group):
    mob = choice(s1)
    return dict_mobs[mob]['class'](screen, coords, *(list(dict_mobs[mob].values())[2:]), *group)


dict_mobs = {
    'Zombie': {'class': Zombie, 'id': [1, 26, 30, 2, 4, 21],
               'health': 50, 'armor': 3, 'damage': 6,
               'damage_type': 'обычный', 'damage_resistance': {}, 'speed': 0.8,
               'speed_attack': 0.8, 'len_attack': 20, 'distance_of_vision_hero': 100, 'hard_level': 1},

    'Slime': {'class': Slime, 'id': [2, 4],
              'health': 30, 'armor': 1, 'damage': 4,
              'damage_type': 'обычный', 'damage_resistance': {'вода': 1.3, 'холод': 1.2},
              'speed': 1.1, 'speed_attack': 1.3, 'len_attack': 15, 'distance_of_vision_hero': 100, 'hard_level': 1},

    'Wolf': {'class': Wolf, 'id': [26, 30, 2, 10, 15, 4],
             'health': 40, 'armor': 2, 'damage': 5,
             'damage_type': 'обычный', 'damage_resistance': {'холод': 1.3},
             'speed': 1.2, 'speed_attack': 1,
             'len_attack': 23, 'distance_of_vision_hero': 120, 'hard_level': 1},

    'Rock': {'class': Rock, 'id': [9],
             'health': 300, 'armor': 5, 'damage': 0,
             'damage_type': '', 'damage_resistance': {},
             'speed': 0, 'speed_attack': 0, 'len_attack': 0,
             'distance_of_vision_hero': 0, 'hard_level': 1},
    'Iron': {'class': Iron, 'id': [40],
             'health': 300, 'armor': 5, 'damage': 0,
             'damage_type': '', 'damage_resistance': {},
             'speed': 0, 'speed_attack': 0, 'len_attack': 0,
             'distance_of_vision_hero': 0, 'hard_level': 1},
    'Gold': {'class': Gold, 'id': [39],
             'health': 300, 'armor': 5, 'damage': 0,
             'damage_type': '', 'damage_resistance': {},
             'speed': 0, 'speed_attack': 0, 'len_attack': 0,
             'distance_of_vision_hero': 0, 'hard_level': 1},
    'Silver': {'class': Silver, 'id': [42],
             'health': 300, 'armor': 5, 'damage': 0,
             'damage_type': '', 'damage_resistance': {},
             'speed': 0, 'speed_attack': 0, 'len_attack': 0,
             'distance_of_vision_hero': 0, 'hard_level': 1},
    'Bronze': {'class': Bronze, 'id': [41],
             'health': 300, 'armor': 5, 'damage': 0,
             'damage_type': '', 'damage_resistance': {},
             'speed': 0, 'speed_attack': 0, 'len_attack': 0,
             'distance_of_vision_hero': 0, 'hard_level': 1},
    'Charcoal': {'class': Charcoal, 'id': [23],
                 'health': 400, 'armor': 5, 'damage': 0,
                 'damage_type': '', 'damage_resistance': {},
                 'speed': 0, 'speed_attack': 0, 'len_attack': 0,
                 'distance_of_vision_hero': 0, 'hard_level': 1},
    'Archer': {'class': Archer, 'id': [26, 30, 2, 10, 15, 4, 28, 32, 36, 22],
               'health': 50, 'armor': 2, 'damage': 7,
               'damage_type': 'обычный', 'damage_resistance': {},
               'speed': 1.1, 'speed_attack': 1, 'len_attack': 200,
               'distance_of_vision_hero': 150, 'hard_level': 1},
    'NPC': {'class': NPC, 'id': [],
            'health': 50, 'armor': 2, 'damage': 7,
            'damage_type': 'обычный', 'damage_resistance': {},
            'speed': 1.1, 'speed_attack': 1, 'len_attack': 200,
            'distance_of_vision_hero': 150, 'hard_level': 1},
    'Goblin': {'class': Goblin, 'id': [26, 30, 2, 10, 15, 4, 21],
               'health': 50, 'armor': 3, 'damage': 6,
               'damage_type': 'обычный', 'damage_resistance': {}, 'speed': 0.8,
               'speed_attack': 0.8, 'len_attack': 20, 'distance_of_vision_hero': 100, 'hard_level': 1},
    'BOS_1': {'class': BOS_1, 'id': [24, 25],
              'health': 500, 'armor': 4, 'damage': 8,
              'damage_type': 'обычный', 'damage_resistance': {}, 'speed': 0.8,
              'speed_attack': 0.8, 'len_attack': 500, 'distance_of_vision_hero': 1000, 'hard_level': 1},
    'SnowMag': {'class': SnowMag, 'id': [37, 29, 20, 35],
                'health': 50, 'armor': 3, 'damage': 10,
                'damage_type': 'обычный', 'damage_resistance': {},
                'speed': 0.7, 'speed_attack': 1, 'len_attack': 200,
                'distance_of_vision_hero': 150, 'hard_level': 2},
    'BOS_2': {'class': BOS_2, 'id': [35, 34, 37, 20],
              'health': 600, 'armor': 7, 'damage': 10,
              'damage_type': 'обычный', 'damage_resistance': {}, 'speed': 0.8,
              'speed_attack': 0.8, 'len_attack': 500, 'distance_of_vision_hero': 1000, 'hard_level': 2},
    'IceWolf': {'class': IceWolf, 'id': [37, 29, 20, 35, 22],
                'health': 50, 'armor': 3, 'damage': 7,
                'damage_type': 'cold', 'damage_resistance': {'холод': 1.3},
                'speed': 1.2, 'speed_attack': 1,
                'len_attack': 26, 'distance_of_vision_hero': 120, 'hard_level': 2},
    'BOS_3': {'class': BOS_3, 'id': [35, 34, 38, 27, 14, 20],
              'health': 600, 'armor': 4, 'damage': 2,
              'damage_type': 'обычный', 'damage_resistance': {}, 'speed': 0.8,
              'speed_attack': 1.2, 'len_attack': 500, 'distance_of_vision_hero': 1000, 'hard_level': 1},
}
