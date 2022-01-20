from math import sqrt

import items.functions as funcs
import pygame
import sqlite3
from random import choice, randint
from objects.object import load_image, COLLIDE_OBJECTS
import threading

MONEY = (6, 7, 8)


class Inventar:
    def __init__(self):
        inventory_list = funcs.list_()
        self.MAX_OBJECTS_IN_INVENTAR = 30

    def take_item(self, item):
        s1 = funcs.quer('player\player.sql',
                        f"select id,name,count from items where id like '{item.id}%'")
        s2 = funcs.quer('player\player.sql', f"SELECT id from items")

        if s1 and s1[0] and s1[0][1]:
            if s1[-1][-1] + item.elems['counts'] > item.elems['limit']:
                if s1[-1][0] in MONEY[1:]:
                    Money.change(None, s1[-1][0], s1[-1][-1], item.elems['counts'])
                else:
                    funcs.quer('player\player.sql',
                               F"UPDATE items SET count = '{item.elems['limit']}' where id = '{s1[-1][0]}'")
                    if len(s2) < self.MAX_OBJECTS_IN_INVENTAR:
                        funcs.quer('player\player.sql',
                                   F"INSERT into items(id,count,name) VALUES('{s1[-1][0] + 0.01}',"
                                   F"'{item.elems['counts'] - item.elems['limit'] % s1[-1][-1]}','{s1[-1][1]}')")
            else:
                funcs.quer('player\player.sql',
                           F"UPDATE items SET count = '{s1[-1][-1] + item.elems['counts']}' where id = '{s1[-1][0]}'")
        else:
            if len(s2) < self.MAX_OBJECTS_IN_INVENTAR:
                funcs.quer('player\player.sql',
                           F"INSERT into items(id,count,name) VALUES('{item.id}.0','{item.elems['counts']}','"
                           F"{item.elems['name']}')")


class Items(pygame.sprite.Sprite):
    SPRITE_ITEMS = pygame.sprite.Group()
    BASE = 'items\items.sql'
    inventar = Inventar()

    def __init__(self, index, pos, level=None):
        super().__init__(Items.SPRITE_ITEMS)
        res = funcs.all_names()
        query = f'SELECT * from {res[0]}'
        for i in range(1, len(res)):
            query += f' LEFT JOIN {res[i]} on {res[i - 1]}.id = {res[i]}.id'
        query += f" where {res[0]}.id = '{index}'"
        s1 = funcs.quer(Items.BASE, query)
        if s1:
            s1 = s1[0]
            name = sqlite3.connect('items\items.sql').execute(query)
            names = list(map(lambda x: x[0], name.description))
            name.close()
            self.elems = {}
            for i in range(len(names)):
                self.elems[names[i]] = s1[i]
            self.elems['color'] = funcs.change_color(self.elems['rarity'])
            self.elems['counts'] = 1
            self.image = load_image(self.elems['image'])
            self.image = pygame.transform.scale(self.image, (25, 25))
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]
            self.id = self.elems['id']
            self.time_kill = 0
            self.count = 0
        else:
            self.kill()

    def take(self):
        Items.inventar.take_item(self)
        self.time_kill = self.count

    def get_random_item(self, indexes):
        if not indexes:
            raise ValueError('не переданы возможные индексы мобов')
        indexes = map(str, list(indexes))
        item_types = {(0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                       *(i for i in range(26, 999))): Items, MONEY: Money}
        asd = list(map(lambda x: funcs.change_((x[0], 100 / x[1])),
                       funcs.quer(Items.BASE, f"SELECT id,rarity from item where id in ({','.join(indexes)})")))

        for i in range(len(asd)):
            for key in item_types.keys():
                if asd[i] in key:
                    asd[i] = asd[i], item_types[key]
        return asd

    def update(self, hero, pos=(), kill=False):
        if kill:
            self.kill()
            return None
        self.count += 1
        if not hero:
            raise ValueError('не передан игрок')
        if not self.time_kill:
            if self.count > 240:
                self.kill()
            if (pygame.sprite.collide_mask(self, hero) or (
                    pos and self.rect.collidepoint(*pos) and (hero.rect.x - self.rect.x) ** 2 + (
                    hero.rect.y - self.rect.y) ** 2 <= 100 ** 2)) and self.count > 1:
                self.take()
        elif self.count - 60 <= self.time_kill:
            self.image = pygame.Surface((0, 0))
            font = pygame.font.Font(None, 25)

            name = self.elems['name'] if self.elems['name'] else 'нет названия'
            surface = pygame.Surface((len(name) * 10 + 15, 30))
            text = font.render(f'{name}', False, pygame.Color(f'{self.elems["color"]}'))
            surface.blit(text, (
                (surface.get_width() - text.get_width()) // 2, (surface.get_height() - text.get_height()) // 2))
            surface.set_alpha(100)
            self.image = surface
        else:
            self.kill()


class Money(Items):
    def __init__(self, index, pos, level, count=None):
        super().__init__(index, pos)
        if not count:
            self.elems["counts"] = int(randint(1, 15) * sqrt(level))
        else:
            self.elems['counts'] = count
        if self.elems['name'].startswith('золот'):
            self.elems['color'] = 'gold'
            self.elems['counts'] = 2 if self.elems['counts'] > 16 else 1
        elif self.elems['name'].startswith('сер'):
            self.elems['color'] = 'white'
            self.elems["counts"] = min(1, self.elems['counts'] // 3)
        else:
            self.elems['color'] = 'brown1'

    def change(self, index, old_count, new_count):
        if new_count + old_count > 100:
            funcs.quer('player\player.sql',
                       f"""UPDATE items SET count = '{(new_count + old_count) % 100}' where id = '{index}'""")
        elif new_count + old_count == 100:
            funcs.quer('player\player.sql', f"DELETE from items where id='{index}'")
        else:
            funcs.quer('player\player.sql',
                       f"""UPDATE items SET count = '{(new_count + old_count) % 100}' where id = '{index}'""")
        s1 = funcs.quer('player\player.sql',
                        f"select id,count,name from items where id like '{index - 1}%'")
        name = ''
        if index == 8:
            name = 'серебряные монеты'
        elif index == 7:
            name = 'золотые монеты'

        if not s1 or not s1[0]:
            funcs.quer('player\player.sql',
                       F"INSERT into items(id,count,name) VALUES('{index - 1}.0','1','{name}')")
        else:
            funcs.quer('player\player.sql',
                       F"UPDATE items SET count = '{s1[-1][1] + new_count}' where id = '{s1[-1][0]}'")


def buy_object(object_name, price=None):
    s1 = funcs.quer('player\player.sql',
                    f"select count from items where id in ('6','7','8')")
    sum_ = 0
    for i in range(len(s1)):
        sum_ += s1[i][0] * 100 ** i
    cost = price
    if sum_ < cost:
        return False
    add_item(object_name)
    sum_ -= cost
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


def traiding_to_money(object_name):
    funcs.traiding_to_money(object_name)


def add_item(name):
    id = funcs.quer('items\items.sql', F"""SELECT item.id FROM item
         LEFT JOIN names on names.id = item.id
          where name = '{name}'""")
    if id and id[0] and id[0][0]:
        item = Items(id[0][0], (2000, 2000))
        item.take()

def del_item(name):
    funcs.del_item(name)
