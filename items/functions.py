import sqlite3
from math import cos, sin, radians
from random import randint, choice
import pygame
import csv
from objects.object import load_image, COLLIDE_OBJECTS

GROUP_TILES = pygame.sprite.Group()
gravity = 0.35


def set_group_tiles(new_group):
    global GROUP_TILES
    s1 = list(filter(lambda x: x.id in COLLIDE_OBJECTS, [i for i in new_group]))
    GROUP_TILES = pygame.sprite.Group()
    for i in s1:
        GROUP_TILES.add(i)
    return GROUP_TILES


MONEY = {6: 'gold1', 7: 'whitesmoke', 8: 'tan1'}


def equip(name=''):
    s = f"WHERE name = '{name}'" if name else ''
    s1 = quer('items\items.sql', F"""SELECT names.name,damage,len_attack,type_damage from weapon
INNER JOIN names on names.id = weapon.id {s}""")
    if name and s1:
        return s1[0]
    s2 = quer('items\items.sql', F"""SELECT names.name,armor,CD from armor
INNER JOIN names on names.id = armor.id {s}""")
    if name and s2:
        return s2[0]
    return s1, s2


def traiding_to_money(object_name):
    d1 = quer('player\player.sql', F"""select id,count from items where name = '{object_name}'""")
    if d1 and d1[0] and int(d1[0][0]) not in (6, 7, 8):
        id_, count_ = d1[-1]
        cost = quer('items\items.sql', F"""SELECT cost from item where id = '{int(id_)}'""")[0][0]
        sum_ = 0
        s_ = list(map(lambda x: x[0], quer('player\player.sql',
                                           f"select count from items where id in ('6','7','8')")))
        for i in range(len(s_)):
            sum_ += s_[i] * 100 ** i
        if count_ > 1:
            quer('player\player.sql', f"UPDATE items SET count = '{count_ - 1}' where id='{id_}'")
        elif count_ == 1:
            quer('player\player.sql', f"DELETE from items where id='{id_}'")
        sum_ += cost
        b = sum_ % 100
        si = (sum_ % 10000) // 100
        g = sum_ // 10000
        for count, index, name in ((b, 8, 'медные монеты'), (si, 7, 'серебряные монеты'), (g, 6, 'золотые монеты')):
            if count:
                s1 = quer('player\player.sql',
                          f"""SELECT count from items where id = '{index}'""")
                if not s1:
                    quer('player\player.sql',
                         f"INSERT into items(id,count,name) VALUES('{index}','{0}','{name}')")
                quer('player\player.sql',
                     f"UPDATE items SET count = '{count}' where id='{index}'")


def armor_on_hero():
    name = sqlite3.connect('player\player.sql').execute('SELECT * from equip')
    names = list(map(lambda x: x[0], name.description))[1:]
    d1 = []
    for i in names:
        d1.append(quer('player\player.sql', f"""SELECT {i} FROM equip""")[0][0])
    name.close()
    k = '('
    for i in range(len(d1)):
        k += '"' + str(d1[i]) + '"'
        if i != len(d1) - 1:
            k += ','
    k += ')'
    s1 = quer('items\items.sql', F"""SELECT * from item
     LEFT join names on names.id = item.id 
     where name in {k}""")
    d1 = {}
    for i in range(len(s1)):
        eq = equip(s1[i][-1])
        d1[s1[i][6]] = [s1[i][1], s1[i][-1], eq[-1], eq[2], change_color(s1[i][2]), s1[i][0], eq[1], change_armor]
    return d1


def change_armor(hero=None, index='', pos=None, game=None):
    if not index:
        raise IndexError('нет название')
    s1 = quer('player\player.sql', f"""SELECT * from items""")
    if index not in map(lambda x: x[2], s1):
        raise IndexError(f'элемента {index} нет в инвентаре')
    else:
        name1 = index
        index = s1[list(map(lambda x: x[2], s1)).index(f'{index}')][0]
        name = quer('items\items.sql', f"""SELECT equip from item
         LEFT join names on names.id = item.id 
         where name='{name1}' """)[0][0]
        old_ = quer('player\player.sql', F"""SELECT {name} from equip""")[0][0]
        old_index = quer('items\items.sql', F"""SELECT id from names where name = '{old_}'""")[0][0]
        quer('player\player.sql', f"DELETE FROM items where id = '{index}' ")
        quer('player\player.sql',
             f"""INSERT into items(id,count,name) VALUES('{old_index}.{randint(0, 7)}{randint(1, 8)}','{1}',
        '{old_}')""")
        quer('player\player.sql', F"""update equip SET '{name}' = '{name1}'""")


def all_names():
    res = 'item', 'names'
    return res


def list_(new_quer=None):
    if not new_quer:
        querye = f"""SELECT id,count from items"""
    else:
        k = '('
        for i in range(len(new_quer)):
            k += '"' + str(new_quer[i]) + '"'
            if i != len(new_quer) - 1:
                k += ','
        k += ')'
        querye = f"""SELECT id,count from items where name in {k}"""
    s1 = quer('player\player.sql', querye)
    res = all_names()
    asqwedas = 0
    k = 0
    for j in range(len(s1)):
        j = j - k
        query = 'SELECT image,name,rarity,cost from item'
        if s1[j] and len(s1[j]) > 1 and not s1[j][0] is None:
            for i in range(1, len(res)):
                if res[i]:
                    asqwedas = i
                    query += f' LEFT JOIN {res[i]} on {res[i - 1]}.id = {res[i]}.id'
            query += f" where {res[asqwedas]}.id = '{int(s1[j][0])}'"
            s2 = quer('items\items.sql', query)
            function = no_func

            if int(s1[j][0]) in func_cor.keys():
                function = func_cor[int(s1[j][0])]
            color = None
            if not s2:
                s2 = [(None, None)]
            else:
                if int(s1[j][0]) not in MONEY.keys():
                    color = change_color(s2[0][-2])
                else:
                    color = MONEY[s1[j][0]]
            s1[j] = (*s2[0], color, *s1[j], function)
        else:
            del s1[j]
            k += 1
    return s1


def no_func(hero=None, index='', pos=None, game=None):
    return None


def heal_potion(hero=None, index='', pos=None, game=None):
    if not hero:
        raise ValueError('не передан игрок')
    if not index:
        raise ValueError('не передан индекс')
    s1 = quer('items\items.sql', f"""SELECT Heffects from item
                                 LEFT JOIN names on item.id = names.id 
                                 where name = '{index}'""")
    if hero.health != hero.max_health:
        if s1 and del_item(index):
            hero.health = min(hero.max_health, hero.health + hero.max_health // 100 * s1[0][0])

    return hero.health


def del_item(index):
    s2 = quer('player\player.sql', f"""SELECT id,count from items where name = '{index}' """)
    if s2 and s2[0]:
        if s2[-1][-1] > 1:
            quer('player\player.sql', f"""UPDATE items set count = '{s2[-1][-1] - 1}' where id = '{s2[-1][0]}'""")
        elif s2[-1][-1] == 1:
            quer('player\player.sql', f"""DELETE from items where id = '{s2[-1][0]}'""")
        else:
            return None
    else:
        return None
    return True


def teleport(hero, pos, index='', game=None):
    if not hero:
        raise ValueError('не передан игрок')
    if not pos:
        raise ValueError('не передана позиция телепорта')
    hero.rect.x = pos[0]
    hero.rect.y = pos[1]


def teleport_on_house(hero=None, index='', pos=None, game=None):
    if not game:
        raise ValueError('не передан game')
    game.floor.rooms[game.floor.current_room].clear()
    game.floor.current_room = 2
    game.player_group.sprites()[0].rect.x = 600
    game.player_group.sprites()[0].rect.y = 400


def change_(s1):
    if randint(0, 10000) < s1[1] * 100:
        return s1[0]
    return 0


def quer(base, query):
    if not base:
        raise ValueError('не передана база данных')
    if not query:
        raise ValueError('не передан запрос')
    con = sqlite3.connect(base)
    cur = con.cursor()
    res = cur.execute(f"""{query}""").fetchall()
    con.commit()
    con.close()
    return res


def change_color(x):
    if x <= 15:
        color = 'white'
    elif x <= 20:
        color = 'cyan'
    elif x <= 35:
        color = 'yellow'
    elif x <= 65:
        color = 'violet'
    elif x <= 85:
        color = 'red'
    else:
        color = 'orange'
    return color


class Fire(pygame.sprite.Sprite):
    def __init__(self, pos, type, damage,
                 surf, attack=False, death_time=360, destroy=5, v=None, *group):
        super().__init__(*group)
        self.rect = surf.get_rect()
        self.damage = damage
        self.rect.x, self.rect.y = pos[0] + 15, pos[1] + 25
        self.image = surf
        self.mask = pygame.mask.from_surface(self.image)
        self.count = 0
        self.armor = 1000
        self.type = type
        self.x = self.rect.x
        self.y = self.rect.y
        self.v = v
        self.size = self.rect.width, self.rect.height
        self.attack = attack
        self.death_time = death_time
        self.destroy = destroy

    def update(self, hero):
        if not self.v:
            self.find_vector(hero)
        self.count += 1
        self.x += self.v[0]
        self.y += self.v[1]
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)
        self.collide_check(hero)

    def todark(self, vis):
        pass

    def find_vector(self, hero):
        v = hero.rect.x + 15, hero.rect.y + 20
        v = pygame.math.Vector2(v)
        v1 = pygame.math.Vector2((self.rect.x, self.rect.y))
        angle = round((v - v1).as_polar()[1], 5)
        self.v = 2 * cos(radians(angle)), 2 * sin(radians(angle))

    def collide_check(self, hero):
        if self.count == self.death_time or pygame.sprite.spritecollideany(self, GROUP_TILES):
            self.kill()
        else:
            if self.attack:
                if pygame.sprite.collide_mask(hero, self):
                    hero.take_damage(self.damage, self.type)
                    self.kill()
            else:
                for i in self.groups()[-1]:
                    if not isinstance(i, Fire) and i.armor < 50:
                        if pygame.sprite.collide_mask(self, i):
                            i.take_damage(self.damage, damage_type=f'{self.type}')
                            self.kill()

    def kill(self):
        groups = self.groups()
        if groups:
            if len(groups) > 1:
                group = groups[1]
            else:
                group = groups[0]
            for i in range(self.destroy):
                group.add(destroyedObject(self.image, (self.rect.x, self.rect.y), 2, speed=1))
        super().kill()


class fire_group(pygame.sprite.Group):
    def __init__(self, pos, damage, type, surf, n=36, s_angle=0, k=10, speed_k=2.5, attack=False, *group):
        super().__init__(*group)
        for i in range(n):
            v = (round(cos(radians(i * k + s_angle)), 5) * speed_k, round(sin(radians(i * k + s_angle)), 5) * speed_k)
            self.add(Fire((pos[0] + 20, pos[1] + 20), type, damage / 2,
                          pygame.transform.rotate(surf, 270 - (i * k + s_angle)), attack=attack, v=v))


def fire_surf(x=7):
    surf = pygame.Surface((x * 2, x * 2), pygame.SRCALPHA, 32)
    pygame.draw.lines(surf, pygame.Color('firebrick'), True,
                      [(surf.get_width() / 2, surf.get_height() / 4),
                       (0, surf.get_height()),
                       (surf.get_width(), surf.get_height())], 3)
    pygame.draw.lines(surf, pygame.Color('orangered1'), True,
                      [(surf.get_width() / 2, surf.get_height() * 0.4),
                       (1 / 4 * surf.get_width(), surf.get_height()),
                       (surf.get_width() * 3 / 4, surf.get_height())], 2)
    pygame.draw.lines(surf, pygame.Color('gold1'), True,
                      [(surf.get_width() / 2, surf.get_height() / 3 * 2),
                       (1 / 3 * surf.get_width(), surf.get_height()),
                       (surf.get_width() * 2 / 3, surf.get_height())], 2)
    return surf


def snow_surf(x=7):
    surf = pygame.Surface((x * 2, x * 2), pygame.SRCALPHA, 32)
    pygame.draw.circle(surf, pygame.Color('cyan2'), (x, x), x)
    return surf


def fakel(hero=None, index='', pos=None, game=None):
    if del_item(index):
        cur_rum = game.floor.current_room
        surf = fire_surf()
        game.floor.rooms[cur_rum].enemies_group.add(fire_group((hero.rect.x, hero.rect.y), 50, 'fire', surf))


def Snowflake(hero=None, index='', pos=None, game=None):
    if del_item(index):
        cur_rum = game.floor.current_room
        surf = snow_surf()
        game.floor.rooms[cur_rum].enemies_group.add(fire_group((hero.rect.x, hero.rect.y), 50, 'cold', surf))


def posion(hero=None, index='', pos=None, game=None):
    if del_item(index):
        cur_rum = game.floor.current_room
        surf = pygame.Surface((7 * 2, 7 * 2), pygame.SRCALPHA, 32)
        width, height = 7, 7
        pygame.draw.circle(surf, pygame.Color('chartreuse4'), (width, height), width)
        pygame.draw.circle(surf, pygame.Color('green'), (width, height), width, 1)
        pygame.draw.circle(surf, pygame.Color('chartreuse'), (width, height), width // 2)
        surf.set_alpha(100)
        game.floor.rooms[cur_rum].enemies_group.add(fire_group((hero.rect.x, hero.rect.y), 50, 'potion',surf))


def electric_surf(width=7):
    width, height = width, width
    surf = pygame.Surface((width * 2, width * 2), pygame.SRCALPHA, 32)
    pygame.draw.circle(surf, pygame.Color('grey93'), (width, height), width, round(width / 7))
    pygame.draw.lines(surf, pygame.Color('grey93'), False, [(0, height), (width, height), (width * 2, 0)],
                      round(width / 7 * 3))
    pygame.draw.lines(surf, pygame.Color('lightslateblue'), False, [(0, height), (width, height),
                                                                    (width * 2, height * 2), (width, height),
                                                                    (width * 2, 0)], round(width / 7 * 2))
    surf.set_alpha(150)
    return surf


def electric_sphere(hero=None, index='', pos=None, game=None):
    if del_item(index):
        cur_rum = game.floor.current_room
        surf = electric_surf()
        game.floor.rooms[cur_rum].enemies_group.add(fire_group((hero.rect.x, hero.rect.y), 50, 'electric', surf))


def add_arrow(pos, type, damage, pos_2, attack=False, death_time=360, *group):
    v = pygame.Vector2(pos_2) - pygame.Vector2(pos)
    destroy = 0
    surf = pygame.Surface((30, 30), pygame.SRCALPHA, 32)
    pygame.draw.line(surf, pygame.Color('brown'), (0, 15), (30, 15), 3)
    pygame.draw.lines(surf, pygame.Color('white'), True, [(30, 10), (30, 20), (25, 15)], 5)
    pygame.draw.lines(surf, pygame.Color('gold'), True, [(5, 12), (5, 18), (0, 15)], 3)
    surf = pygame.transform.rotate(surf, (180 - v.as_polar()[-1]) % 360)
    angle = v.as_polar()[-1]
    Fire(pos, type, damage, surf, attack,
         death_time, destroy, (2 * cos(radians(angle)), 2 * sin(radians(angle))), *group)


class Check_line(pygame.sprite.Sprite):
    def __init__(self, screen, radius, pos, x_h, y_h, w_h, h_h, parent=None):
        super().__init__()
        self.parent = parent
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA, 32)
        self.rect = pygame.Rect(*pos, radius * 2, radius * 2)

        coox, cooy = (x_h + w_h // 2) - (pos[0] + self.image.get_width() // 2), (y_h + h_h // 2) - (
                pos[1] + self.image.get_height() // 2)
        pygame.draw.line(self.image, pygame.Color('black'), (self.image.get_width() // 2, self.image.get_height() // 2),
                         (self.image.get_width() // 2 + coox, self.image.get_height() // 2 + cooy), 1)
        self.mask = pygame.mask.from_surface(self.image)

    def check_direct(self):
        for sprite in GROUP_TILES:
            if pygame.sprite.collide_mask(self, sprite) and sprite != self.parent:
                return False
        return True

    def todark(self, vis):
        pass


class destroyedObject(pygame.sprite.Sprite):
    def __init__(self, image, pos, parts, speed=1.0, death_time=30, *groups):
        dx, dy = randint(-5, 5) * speed, randint(-8, -3) * speed
        image = load_image(image) if not type(image) == pygame.Surface else image
        self.size = image.get_width(), image.get_height()
        self.part = [image]
        for scale in (i * 3 for i in range(1, parts + 1)):
            self.part.append(pygame.transform.scale(self.part[0], (scale, scale)))
        del self.part[0]
        super().__init__(*groups)
        self.death_time = death_time
        self.armor = 20000
        self.image = choice(self.part)
        self.rect = self.image.get_rect()
        self.vel = [dx, dy]
        self.rect.x, self.rect.y = pos[0] - randint(-30, -10), pos[1] - randint(-30, -10)
        self.count = 0

    def take_damage(self, pos, hero, check=False, damage_type=None):
        pass

    def update(self, hero):
        self.vel[-1] += gravity
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[-1]
        self.count += 1
        if self.count >= self.death_time:
            self.kill()

    def todark(self, vis):
        pass


class mega_snow_boll(Fire):
    def __init__(self, pos, type, damage,
                 surf, attack=True, death_time=150, destroy=15, v=0, *group):
        super().__init__(pos, type, damage,
                         surf, attack=attack, death_time=death_time, destroy=destroy, v=v, *group)
        self.change_set(snow_surf(), type, n=8, s_angle=-10, change_angle=46)

    def change_set(self, surf, type=None, n=0, s_angle=0, change_angle=90):
        self.death_surf = surf
        self.type = type
        self.n = n
        self.s_angle = s_angle
        self.change_angle = change_angle

    def kill(self):
        groups = self.groups()
        if groups:
            if len(groups) > 1:
                group = groups[1]
            else:
                group = groups[0]
            group.add(fire_group((self.rect.x, self.rect.y), 10, 'cold', self.death_surf, self.n, self.s_angle,
                                 self.change_angle,
                                 speed_k=2,
                                 attack=True))
        super().kill()


class pair_ball(Fire):
    def __init__(self, pos, type, damage,
                 surf, attack=True, death_time=1200, destroy=15, cos_=True,
                 voln=False, circle=False, cicrle_times=((0, 0),), v=0, amp=20, frequency=3, *group):
        super().__init__(pos, type, damage,
                         surf, attack=attack, death_time=death_time,
                         destroy=destroy, v=v, *group)
        self.v_x = frequency
        self.v_y = frequency
        self.func, self.func1 = (cos, sin) if cos_ else (sin, cos)
        self.s1 = []
        self.voln = voln
        self.circle = circle
        self.amplitude = amp
        if circle:
            self.cicrle_times = cicrle_times

    def update(self, hero):
        if not self.v:
            self.find_vector(hero)
        self.count += 1
        x = self.count * self.v_x
        y = self.count * self.v_y
        if not self.circle or not any(x[0] < self.count < x[1] for x in self.cicrle_times):
            self.x += self.v[0]
            self.y += self.v[1]
        self.rect.y = round(self.y + round(self.func1(radians(y)), 5) * self.amplitude)
        self.rect.x = round(self.x + round(self.func(radians(x)), 5) * self.amplitude)
        if self.voln:
            self.s1.append((self.rect.x + self.image.get_width() // 2, self.rect.y + self.image.get_height() // 2))
            if len(self.s1) > 35:
                del self.s1[0]
        self.collide_check(hero)


class ships(pygame.sprite.Group):
    def __init__(self, pos, damage, type, surf, n, s_angle=0, death_time=300, speed_k=2.5, attack=True, *group):
        super().__init__(*group)
        self.radius = 15
        self.pos = pos
        self.damage = damage
        self.type = type
        self.surf = pygame.transform.rotate(surf, 180)
        self.n = n
        self.s_angle = s_angle
        self.attack = attack
        self.death_time = death_time
        self.count = 0
        self.add(Fire(pos, self.type, self.damage, pygame.transform.scale(self.surf, (0, 0)), self.attack,
                      self.death_time,
                      v=(0, 0)))

    def loop(self):
        self.count += 1
        for i in self.sprites():
            i.size = i.size[0] + 0.025, i.size[1] + 0.05
            i.rect.x -= 0.00125
            i.rect.y -= 0.025
            i.image = pygame.transform.scale(self.surf, (round(i.size[0]), round(i.size[1])))
            i.rect.width = i.image.get_width()
            i.rect.height = i.image.get_height()
        if not self.sprites()[0].count % 20 and not self.count > self.death_time:
            self.radius += 15
            for i in range(0, 360, round(360 / self.n)):
                anypos = (self.pos[0] + self.radius * round(cos(radians(self.s_angle + i)), 5),
                          self.pos[1] + self.radius * round(sin(radians(self.s_angle + i)), 5))
                self.add(Fire(anypos, self.type, self.damage, self.surf, self.attack, self.death_time, v=(0, 0)))

    def todark(self, vis):
        pass


class line1(pygame.sprite.Sprite):
    def __init__(self, pos, type, damage, color=None, death_time=360, v=1, *group):
        super().__init__(*group)
        if color is None:
            color = pygame.Color('coral1')
        surf = pygame.Surface((5, 2), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, pygame.Color('cyan2'), pos, 3)
        surf.fill(color)
        self.color = color
        self.image = surf
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.type = type
        self.damage = damage * 2
        self.death_time = death_time
        self.count = 0
        self.w = self.rect.width
        self.v = v
        self.armor = 1000
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, hero):
        self.count += 1
        if not self.count % 2 and pygame.sprite.collide_mask(self, hero):
            hero.take_damage(self.damage, self.type)
        if self.count < self.death_time // 3:
            self.w += 0.5
            self.image = pygame.transform.scale(self.image, (round(self.w), 2))
            self.rect.width = self.image.get_width()
            self.mask = pygame.mask.from_surface(self.image)
        else:
            if self.count == self.death_time // 3:
                self.rect.width = self.w * 2
                self.rect.height = self.w * 2
                self.rect.x -= self.w
                self.rect.y -= self.w
            surf = pygame.Surface((self.w * 2, self.w * 2), pygame.SRCALPHA, 32)
            pygame.draw.circle(surf, self.color, (self.w, self.w), 4)
            pygame.draw.line(surf, self.color, (self.w, self.w),
                             (self.w + self.w * sin(radians(90 - self.v * (self.count - self.death_time // 3))),
                              self.w + self.w * cos(radians(90 - self.v * (self.count - self.death_time // 3)))), 2)
            self.image = surf
            self.mask = pygame.mask.from_surface(self.image)

        if self.count > self.death_time * 2:
            self.kill()

    def todark(self, vis):
        pass


class circle_attack(pygame.sprite.Sprite):
    def __init__(self, pos, radius, color='red', death_time=240, *group):
        super().__init__(*group)
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA, 32)
        surf.set_alpha(140)
        pygame.draw.circle(surf, pygame.Color(color), (surf.get_width() // 2, surf.get_height() // 2), radius, 5)
        self.image = surf
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0] - radius, pos[1] - radius
        self.mask = pygame.mask.from_surface(self.image)
        self.count = 0
        self.armor = 10000
        self.death_time = death_time
        self.damage = 1

    def update(self, hero):
        self.count += 1
        if pygame.sprite.collide_mask(self, hero):
            hero.take_damage(self.damage, 'обычный')
        if self.count == self.death_time:
            self.kill()

    def todark(self, vis):
        pass


class parts(pygame.sprite.Sprite):
    image1 = 'items/rock.png'

    def __init__(self, screen, coords, coords2=None, *groups):
        self.image = load_image(parts.image1)
        self.image1 = load_image(parts.image1)
        self.image = pygame.transform.scale(self.image1, (self.image.get_width() * 4,
                                                          self.image.get_height() * 4))
        super().__init__(*groups)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords
        self.coords = coords
        if not coords2:
            self.coords2 = (randint(500, 1300), randint(200, 850))
        else:
            self.coords2 = coords2
        self.screen = screen
        self.count = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.x = self.rect.x
        self.y = self.rect.y
        self.armor = 10000
        self.damage = 50
        self.type = 'cold'

    def update(self, hero):
        self.count += 1
        self.draw()
        self.x += (self.coords2[0] - self.coords[0]) / 75
        self.y += (self.coords2[1] - self.coords[1]) / 75
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)
        if not self.count % 3:
            surf = pygame.transform.smoothscale(self.image1,
                                                (self.image.get_width() * 0.99999, self.image.get_height() * 0.999999))
            self.image = surf
        if self.count >= 75:
            self.kill(hero)

    def draw(self):
        surf = pygame.Surface((80, 80), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, pygame.Color('red'), (surf.get_width() // 2, surf.get_height() // 2), 20)
        surf.set_alpha(100)
        self.screen.blit(surf, (self.coords2[0] - 20, self.coords2[1] - 30))

    def kill(self, hero=None):
        self.mask = pygame.mask.from_surface(self.image)
        if hero:
            if pygame.sprite.collide_mask(self, hero):
                hero.take_damage(self.damage, self.type)
        groups = self.groups()
        if groups:
            if len(groups) > 1:
                group = groups[1]
            else:
                group = groups[0]
            for i in range(10):
                group.add(destroyedObject(self.image, (self.rect.x, self.rect.y), 2, speed=1))
        super().kill()

    def todark(self, vis):
        pass


class rock(pygame.sprite.Sprite):
    imag = 'items/rock.png'
    imag = load_image(imag)

    def __init__(self, screen, coords_1, n=5, time=3, *group):
        self.image = rock.imag
        super().__init__(*group)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords_1
        self.count = 0
        self.screen = screen
        self.armor = 100000
        self.n = n
        self.time = time
        self.wid = self.rect.width
        self.heig = self.rect.height

    def update(self, hero):
        self.count += 1
        self.rect.x -= 0.01 * self.rect.width
        self.rect.y -= 0.01 * self.rect.height
        self.wid += 0.9
        self.heig += 0.9
        self.image = pygame.transform.scale(rock.imag, (round(self.wid), round(self.heig)))
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()
        if self.count == self.time:
            self.kill(hero)

    def kill(self, hero=None):
        if hero:
            group = self.groups()[0]
            for i in range(self.n):
                group.add(parts(self.screen,
                                (self.rect.x + self.rect.width // 5 * i,
                                 self.rect.y + choice([self.rect.height // 5 * j for j in range(4)]))))
                if i > 1:
                    group.add(parts(self.screen,
                                    (self.rect.x + self.rect.width // 5,
                                     self.rect.y + choice([self.rect.height // 5 * j for j in range(4)])),
                                    (hero.rect.x + i * 40, hero.rect.y + i * -40)))
                    group.add(parts(self.screen,
                                    (self.rect.x + self.rect.width // 5,
                                     self.rect.y + choice([self.rect.height // 5 * j for j in range(4)])),
                                    (hero.rect.x + 90 - 40 * i, hero.rect.y + i * -40)))
            groups = self.groups()
            if groups:
                if len(groups) > 1:
                    group = groups[1]
                else:
                    group = groups[0]
                for i in range(100):
                    group.add(destroyedObject('items/rock.png', (
                        self.rect.x + self.rect.width // 2 + randint(
                            -self.rect.width // 4, self.rect.width // 4),
                        self.rect.y + self.rect.height // 2 + randint(
                            -self.rect.height // 4, self.rect.height // 4)),
                                              5, speed=1, death_time=70))
        super().kill()

    def todark(self, vis):
        pass


class Turel(pygame.sprite.Sprite):
    def __init__(self, pos, type, surf, damage, radius, color='white', death_time=700, *group):
        super().__init__(*group)
        self.armor = 1000
        any_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA, 32)
        any_surf.blit(surf, (radius - surf.get_width() // 2, radius - surf.get_height() // 2))
        surf = any_surf.copy()
        pygame.draw.circle(surf, pygame.Color(color), (surf.get_width() // 2, surf.get_width() // 2), radius, 1)
        self.surf = surf
        self.image = self.surf.copy()
        self.color = color
        self.damage = damage
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.type = type
        self.radius = radius
        self.center = ((self.rect.x + radius), (self.rect.y + radius))
        self.count = 0
        self.death_time = death_time

    def todark(self, vis):
        pass

    def update(self, hero):
        self.count += 1
        self.image = self.surf.copy()
        if (hero.rect.x - self.center[0]) ** 2 + (hero.rect.y - self.center[1]) ** 2 <= self.radius ** 2:
            pygame.draw.line(self.image, pygame.Color(self.color),
                             (self.image.get_width() // 2, self.image.get_height() // 2),
                             (hero.rect.x + 15 - self.rect.x, hero.rect.y + 15 - self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if not self.count % 3 and pygame.sprite.collide_mask(self, hero):
            hero.take_damage(self.damage, self.type)
        if self.count == self.death_time:
            self.kill()

    def kill(self):
        groups = self.groups()
        if groups:
            if len(groups) > 1:
                group = groups[1]
            else:
                group = groups[0]
            for i in range(10):
                group.add(destroyedObject(self.image, (
                    self.rect.x + self.rect.width // 2 + randint(
                        -self.rect.width // 4, self.rect.width // 4),
                    self.rect.y + self.rect.height // 2 + randint(
                        -self.rect.height // 4, self.rect.height // 4)),
                                          5, ))
        super(Turel, self).kill()


class Molny(Fire):
    def __init__(self, pos, type, damage,
                 surf, attack=False, death_time=360, destroy=5, v=None, *group):
        v1 = pygame.math.Vector2(v) - pygame.math.Vector2(pos)
        angle = radians(v1.as_polar()[1])
        self.radius = 5
        surf = pygame.Surface((8 * self.radius, 8 * self.radius), pygame.SRCALPHA, 32)
        self.d1 = [(surf.get_width() // 2, surf.get_height() // 2),
                   (surf.get_width() // 2 + self.radius * cos(angle),
                    surf.get_height() // 2 + self.radius * sin(angle))]
        pygame.draw.line(surf, pygame.Color('white'),
                         *self.d1, 1)
        super(Molny, self).__init__(pos, type, damage,
                                    surf, attack=attack, death_time=death_time, destroy=destroy, v=None, *group)

    def update(self, hero):
        self.count += 1
        if not self.v:
            self.find_vector(hero)
        if not self.count % 2:
            v1 = pygame.math.Vector2((hero.rect.x + 15, hero.rect.y + 15)) - pygame.math.Vector2(
                (self.rect.x + self.d1[-1][0], self.rect.y + self.d1[-1][1]))
            angle = radians(v1.as_polar()[1])
            if len(self.d1) == 3:
                x_ = self.d1[0][0] - self.rect.width // 2
                y_ = self.d1[0][1] - self.rect.height // 2
                self.rect.x += x_
                self.rect.y += y_
                self.d1 = list(map(lambda x: (x[0] - x_, x[1] - y_), self.d1))
                del self.d1[0]
            self.d1.append((self.d1[-1][0] + self.radius * cos(angle), self.d1[-1][1] + self.radius * sin(angle)))

            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA, 32)
            pygame.draw.lines(surf, pygame.Color('white'), False, self.d1, 1)
            self.image = surf
            self.mask = pygame.mask.from_surface(self.image)
            self.collide_check(hero)

def frozen_key(hero=None, index='', pos=None, game=None):
    con = sqlite3.connect("player/player.sql")
    cur = con.cursor()
    cur.execute(f"""UPDATE opened_floors SET status = 1 WHERE floor_id = 1""").fetchall()
    con.commit()
    con.close()
    savings = game.read_savings()
    savings[1][0] = "1"
    with open('savings.csv', 'w', newline='') as csvfile:
        writer = csv.writer(
            csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in savings:
            writer.writerow(row)
    game.del_item("Ледяной Ключ")
    game.generate_floor()


func_cor = {4: heal_potion,
            99: teleport,
            5: teleport_on_house,
            10: change_armor,
            1: change_armor,
            3: change_armor,
            11: change_armor,
            12: change_armor,
            13: change_armor,
            14: change_armor,
            15: fakel,
            20: Snowflake,
            21: posion,
            22: electric_sphere,
            25: change_armor,
            24: frozen_key,
            26: change_armor,
            27: change_armor,
            28: change_armor,
            29: change_armor,
            30: change_armor,
            31: change_armor,
            32: change_armor,
            33: change_armor,
            34: change_armor,
            35: change_armor,
            36: change_armor,
            37: change_armor,
            38: change_armor,

            }
