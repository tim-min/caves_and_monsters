import pygame
from math import sqrt
from objects.object import load_image
from objects.object import COLLIDE_OBJECTS
from objects.object import FUNCTIONAL_OBJECTS
from gui_elements import UI_ELEMENTS
import csv
from random import randint
import sqlite3
from items import items, functions as funcs


class Player(pygame.sprite.Sprite):
    image_up = load_image("player_up.png")
    def __init__(self, screen, game_fps, tile_size, sounds_volume, *group):
        super().__init__(*group)
        self.frames = [self.cut_sheet(load_image("player/walk_up.png"), 9, 1, 64, (40, 55)),
                       self.cut_sheet(load_image("player/walk_down.png"), 9, 1, 63.4, (42, 59)),
                       self.cut_sheet(load_image("player/walk_left.png"), 9, 1, 64, (44, 55)),
                       self.cut_sheet(load_image("player/walk_right.png"), 9, 1, 64, (44, 55)),
                       self.cut_sheet(load_image("player/die.png"), 6, 1, 64, (44, 55))]  # все анимации игрока
        self.rest_image = load_image("player/rest.png")  # стоит на месте
        self.image = self.frames[0][0]
        self.current_animation = 0  # какая сейчас анимация
        self.current_frame = 0  # какой сейчас фрэйм
        self.rect = self.image.get_rect()
        self.rect.height -= 20
        self.rect.x = 300
        self.game_tile_size = tile_size
        self.rect.y = 200
        self.max_health = 150
        self.health = 150
        self.damage_string = ["", (None, None)]
        self.simple_speed = 200 / game_fps  # обычныя скорость
        self.speed = 200 / game_fps  # скорость на данный момент
        self.armor = 0
        self.m_x, self.m_y = 0, 0
        self.game_fps = game_fps
        self.collide_direction = [0, 0, 0, 0]
        self.attack_distance = 100
        self.screen = screen
        self.rect.x, self.rect.y = self.screen.get_width() / 2 - 41 * tile_size / 2 + 100, self.screen.get_height() / 2 - 36 * tile_size / 2 + 13 * tile_size
        self.damage = 8
        self.damage_type = "обычный"
        self.mask = pygame.mask.from_surface(self.image)
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        self.fps_count = 0
        self.death_anim = False
        self.death = False
        self.speed_changed = False
        self.walking_sound = pygame.mixer.Sound("sounds/player/walk.ogg")
        self.hitting_sound = pygame.mixer.Sound("sounds/player/hit.ogg")
        self.update_stats()
        self.take_damage_functions = {
            'cold': self.freeze,
            'electric': self.electr
        }

    def electr(self):
        pass

    def freeze(self):
        self.speed_changed = True
        self.speed = self.speed // 3
    
    def take_damage(self, damage, type): # получение урона
        if self.take_damage_functions.get(type):
            self.take_damage_functions[type]()
        self.health -= damage

    def update_stats(self):
        armor_el = funcs.armor_on_hero()
        print(armor_el)
        self.damage = armor_el["weapon"][6]
        self.damage_type = armor_el["weapon"][2]
        self.attack_distance = armor_el["weapon"][3]
        self.armor = armor_el["tors"][-2] + armor_el["head"][-2] + armor_el["sheald"][-2]

    def cut_sheet(self, sheet, columns, rows, n,
                  size):  # нужно получать сдвиг (n) и размеры кадра (size), т.к на каждой картинке кадры расположены по разному
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        result = list()
        frame_location = 0  # позиция фрэйма по x, который мы хотим отрезать

        for _ in range(columns):
            result.append(sheet.subsurface(pygame.Rect(
                (frame_location, 0),
                size)))  # отрезаем фрэйм по позициям (y всегда 0 так как у нас только 1 линия) и по размеру
            frame_location += n  # n - сдвиг, чтобы перемещаться по картинке

        return result

    def anim(self):
        if not self.fps_count % 2:
            if self.current_animation > -1:
                self.image = self.frames[self.current_animation][
                    self.current_frame]  # меняем image по анимации и фрэйму
                if self.current_frame < len(
                        self.frames[self.current_animation]) - 1:  # если сейчас не последний фрэйм, то прибавляем
                    self.current_frame += 1
                else:
                    if not self.death_anim:
                        self.current_frame = 0  # если последний, то ставим на первый
                    else:
                        self.death_anim = False
                        self.death = True
            else:
                self.image = self.rest_image  # если id анимации -1, значит игрок сейчас стоит на месте

    def movement(self, objects, game):
        if self.speed_changed:
            if not self.fps_count % 2:
                if self.speed < self.simple_speed:
                    self.speed += 0.1
                else:
                    self.speed_changed = False
        else:
            self.speed = self.simple_speed

        self.current_animation = -1  # устанавливаем анимацию на -1, чтобы он стоял на месте
        keys = pygame.key.get_pressed()
        self.collide_direction = [0, 0, 0, 0]
        for x in objects.sprites():
            if pygame.sprite.collide_mask(self, x) and x.id in COLLIDE_OBJECTS and x.collide_function is None:
                if x.id in FUNCTIONAL_OBJECTS["ACCELERATION"]:  # если тайл под игроком ускоряет, то ускорить игрока
                    self.speed = self.simple_speed * 2
                elif x.id in FUNCTIONAL_OBJECTS["GATE"]:
                    x.image = load_image("opened_gate_tile.png")
                    x.image = pygame.transform.scale(x.image, (game.tile_size, game.tile_size))
                elif x.id in FUNCTIONAL_OBJECTS["FLOORCHANGE_UP"]:
                    savings = game.read_savings()
                    savings[1][0] = str(int(savings[1][0]) + 1)
                    game.screens_group.add(game.loading_screen)
                    with open('savings.csv', 'w', newline='') as csvfile:
                        writer = csv.writer(
                            csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        for row in savings:
                            writer.writerow(row)
                    game.generate_floor()
                    game.screens_group = pygame.sprite.Group()
                elif x.id in FUNCTIONAL_OBJECTS["FLOORCHANGE_DOWN"]:
                    savings = game.read_savings()
                    savings[1][0] = str(int(savings[1][0]) - 1)
                    with open('savings.csv', 'w', newline='') as csvfile:
                        writer = csv.writer(
                            csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        for row in savings:
                            writer.writerow(row)
                    game.generate_floor()
                else:
                    self.rect.x -= self.m_x
                    self.rect.y -= self.m_y
                    return
            elif pygame.sprite.collide_mask(self, x) and x.id in COLLIDE_OBJECTS and x.collide_function is not None:
                if x.collide_function == 1:
                    game.goto_another_room(game.floor.current_room - 1)
                    self.rect.x, self.rect.y = self.screen.get_width() / 2 + 41 * self.game_tile_size / 2 - 200, self.screen.get_height() / 2 - 36 * self.game_tile_size / 2 + 13 * self.game_tile_size
                    for cloud in game.clouds:
                        if cloud.rect.x > 0:
                            cloud.rect.x += 500
                    game.floor.rooms[0].wave = 0
                elif x.collide_function == 2:
                    game.goto_another_room(game.floor.current_room + 1)
                    self.rect.x, self.rect.y = self.screen.get_width() / 2 - 41 * self.game_tile_size / 2 + 100, self.screen.get_height() / 2 - 36 * self.game_tile_size / 2 + 13 * self.game_tile_size
                    for cloud in game.clouds:
                        cloud.rect.x -= 500
                    game.floor.rooms[0].wave = 0
                if game.floor.current_room == 0:
                    game.show_fight_guide = True
                    game.show_walking_guide = False
                    game.fight_guide()
                else:
                    game.show_fight_guide = False
                game.generate_menu()

        self.m_x, self.m_y = 0, 0
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.m_y = -1
            self.current_animation = 0  # устанавливаем новый id анимации
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            if not self.m_y:
                self.m_y = 1
            self.current_animation = 1
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.m_x = -1
            self.current_animation = 2
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            if not self.m_x:
                self.m_x = 1
            self.current_animation = 3

        if self.current_animation != -1:
            if not self.fps_count % 10:
                self.walking_sound.play()

    def attack(self, enemies, mouse_position):
        self.hitting_sound.play()
        for enemy in enemies:
            if sqrt((enemy.rect.x - self.pos[0]) ** 2 + (
                    enemy.rect.y - self.pos[1]) ** 2) <= self.attack_distance and enemy.rect.collidepoint(
                mouse_position):
                if randint(1, 20) >= enemy.armor:
                    damage = randint(1, self.damage)
                    enemy.take_damage(damage, mouse_position, self.damage_type)
                    self.damage_string[0] = "-" + str(damage)  # сохранение надписи об уроне
                    self.damage_string[1] = (enemy.rect.x, enemy.rect.y - 10)  # позиция над мобом

    def draw(self):
        # text = self.font.render(str(self.health) + "hp", True, pygame.Color("white"))
        # self.screen.blit(text, (self.pos[0], self.pos[1] - 20))
        pygame.draw.rect(self.screen, pygame.Color("white"), [self.rect.x, self.rect.y - 20, 50, 10])
        pygame.draw.rect(self.screen, pygame.Color("red"),
                         [self.rect.x, self.rect.y - 20, 50 * self.health // self.max_health, 10])
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (self.pos[0] + 20, self.pos[1] + 20), self.attack_distance, 1)
        if self.damage_string[0]:
            text = self.font.render(self.damage_string[0], True, pygame.Color("white"))
            self.screen.blit(text, self.damage_string[1])

        if self.fps_count % 120 == 0:
            self.damage_string = ["", (0, 0)]

        self.fps_count += 1

    def update(self, objects, game):
        self.walking_sound.set_volume(float(game.sounds_volume))
        self.hitting_sound.set_volume(float(game.sounds_volume))
        if self.health <= 0 and not self.death_anim:
            self.death_anim = True
            self.current_animation = 4
            self.current_frame = 0
        
        if self.death:
            self.death = False
            self.current_animation = -1
            self.death_anim = False
            game.show_die_screen = True
            game.screens_group.add(game.loading_screen)
            game.die_screen_buttons.add(UI_ELEMENTS["button"]((game.screen.get_width() // 2 - 100, game.screen.get_height() // 2 - 200), "Продолжить", game.spawn_player, font_size=25))
            game.die_screen_buttons.add(UI_ELEMENTS["button"]((game.screen.get_width() // 2 - 100, game.screen.get_height() // 2 - 150), "Выйти", game.terminate))
        self.pos = [self.rect.x, self.rect.y]
        self.anim()
        if not self.death_anim:
            self.movement(objects, game)
        self.draw()
    
    def tile_visibility(self, tile, length=100):
        if (tile.rect.x - self.rect.x) ** 2 + (tile.rect.y - self.rect.y) ** 2 <= length ** 2:
            return True
        return False

