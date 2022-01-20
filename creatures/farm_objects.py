from random import randint, choice
from objects.object import load_image
from items.items import Items

import pygame

gravity = 0.40

object_di = {'rock': ['rock_tile.png', 9], 'button': ['button.png', 2]}


class FarmGroupObject(pygame.sprite.Group):
    def __init__(self, health, level, armor, object, coords, count_objects=10):
        super().__init__()
        self.health = health * count_objects
        self.armor = armor
        self.level = level
        self.when = health
        self.count_objects = count_objects
        for i in range(count_objects):
            x = coords[0] + randint(-10, 10)
            y = coords[1] + randint(-10, 10)
            self.add(FarmObject(object, x, y))

    def take_damage(self, damage, pos):
        g = pos
        for i in self.sprites():
            if isinstance(i, FarmObject) and i.rect.collidepoint(g):
                k = 2 if damage < self.armor else 1
                g = choice(self.sprites())
                while not isinstance(g, FarmObject):
                    g = choice(self.sprites())
                if self.health >= (self.count_objects - 1) * self.when and self.health - damage // k < (
                        self.count_objects - 1) * self.when:
                    self.count_objects -= 1
                    for i in range(10):
                        self.add(destroyedObject(g.name_image,(g.x + g.width, g.y + g.height), randint(-5, 5),
                                                 randint(-7, -3),
                                                 3))
                    g.stuff()
                    g.kill()
                else:
                    for i in range(5):
                        self.add(destroyedObject(g.name_image,(g.x + g.width, g.y + g.height), randint(-5, 5),
                                                 randint(-7,
                                                                                                                 -3), 1))
                self.health -= damage // k
                break


class FarmObject(pygame.sprite.Sprite):
    def __init__(self, object_, pos_x, pos_y, *groups):
        self.name_image = object_di[object_][0]
        self.image = load_image(self.name_image)
        self.image = pygame.transform.scale(self.image, (25, 25)) # тут поменял!!!!!
        super().__init__(*groups)

        self.object = object_di[object_][1]
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.mask = pygame.mask.from_surface(self.image)

    def stuff(self):
        Items(self.object, (self.x + self.width * choice([1, -1]), self.y + self.width // 2))

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    @property
    def width(self):
        return self.image.get_width()

    @property
    def height(self):
        return self.image.get_height()





class group_sprite():
    def __init__(self):
        self.groups = []

    @property
    def sprites(self):
        for i in self.groups:
            yield (j for j in i.sprites())

    def timur_bot(self):
        for i in range(10):
            print('TIMUR_BOT')

    def __add__(self, other):
        if isinstance(other, FarmGroupObject):
            self.groups.append(other)

    def append(self, other):
        self.__add__(other)

    def add(self, other):
        self.__add__(other)

    def __delete__(self, item):
        print(item)
        if item >= len(self.groups) or -item > len(self.groups):
            raise IndexError
        else:
            del self.groups[item]

    def __hash__(self):
        return hash(self.groups)

    def __getitem__(self, item):
        if item >= len(self.groups) or -item > len(self.groups):
            raise IndexError
        else:
            return self.groups[item]

    def loop(self, damage, event):
        if pygame.mouse.get_pressed()[0]:
            for i in self.groups:
                i.take_damage(damage, event.pos)

    def update(self):
        for i in range(len(self.groups)):
            self.groups[i].update()
            if not len(self.groups[i].sprites()):
                del self.groups[i]

    def draw(self, screen):
        for i in self.groups:
            i.draw(screen)

    def __str__(self):
        return ' '.join(str(i) for i in self.groups)
