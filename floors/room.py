import pygame
from random import choice, randint
from objects.object import TRANSPARENT_OBJECTS
from objects.object import FUNCTIONAL_OBJECTS
from objects.object import Tile
from items import items, functions as funcs
from random import randint
from gui_elements import NPC
from creatures.enemy import create_mob


class Room:
    def __init__(self, room_settings):
        self.enemy_spawn_ability = room_settings["spawn_ability"]  # могут ли в комнате появляться монстры
        self.all_enemy_types = room_settings["enemies"]  # какие монстры могут появиться в этой комнате
        self.all_enemy_count = room_settings["enemies_max_count"]
        if self.enemy_spawn_ability:
            self.enemy_types = self.all_enemy_types[0]
            self.enemy_max_count = self.all_enemy_count[0]
        if room_settings.get("door_position"):
            self.door_position = room_settings["door_position"]
        if room_settings.get("music"):
            self.music = room_settings["music"]
        self.show_door_up = False
        self.waves_max = room_settings["waves"]  # макс волны мобов
        self.wave = 0
        self.npc_types = room_settings["npc"]
        self.npc_spawn = room_settings["npc_spawn"]
        self.npc_coords = room_settings["npc_coords"]
        self.main_tile = room_settings["main_tile"]
        self.isdark = room_settings["dark"]
        self.wave_text = ''
        self.npc_count = 0
        self.fps_count = 0
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        self.tiles = pygame.sprite.Group()  # тайлы
        self.enemy_count = 0  # сколько монстров сейчас находятся в комнате
        self.enemies_group = pygame.sprite.Group()  # враги
        self.npc_group = pygame.sprite.Group() # нпс
        self.light_tiles = pygame.sprite.Group()
        # фрам объекты
        self.tile_size = 25
        self.map = room_settings["map"]  # карта(путь к txt файлу)
        self.map_list = list()  # карта ввиде списка

    def generate_map(self, objects, screen, tile_size):  # создание карты по txt файлу
        self.tile_size = tile_size
        x_pos, y_pos = screen.get_width() / 2 - 41 * tile_size / 2, screen.get_height() / 2 - 36 * tile_size / 2
        with open(self.map, "r") as file:
            for x in file.readlines():
                for obj in x.split():
                    if obj in TRANSPARENT_OBJECTS:
                        self.tiles.add(Tile(objects[self.main_tile][0], objects[0][1], (x_pos, y_pos), tile_size))
                    if int(obj) in FUNCTIONAL_OBJECTS["LIGHT"]:
                        self.light_tiles.add(Tile(objects[int(obj)][0], objects[int(obj)][1], (x_pos, y_pos), tile_size))
                    if int(obj) in FUNCTIONAL_OBJECTS["FLOORCHANGE_UP"]:
                        if self.show_door_up:
                            self.tiles.add(Tile(objects[int(obj)][0], objects[int(obj)][1], (x_pos, y_pos), tile_size))
                    elif obj == "27":
                        self.tiles.add(Tile(objects[int(obj)][0], objects[int(obj)][1], (x_pos, y_pos), tile_size, collide_func=1))
                    elif obj == "29":
                        self.tiles.add(Tile(objects[int(obj)][0], objects[int(obj)][1], (x_pos, y_pos), tile_size, collide_func=2))
                    else:
                        self.tiles.add(Tile(objects[int(obj)][0], objects[int(obj)][1], (x_pos, y_pos), tile_size))
                    x_pos += tile_size
                y_pos += tile_size
                x_pos = screen.get_width() / 2 - 41 * tile_size / 2
        if self.isdark:
            for tile in self.tiles:
                for light_tile in self.light_tiles:
                    nexto_light_tile = light_tile.in_radius(tile)
                    tile.set_visibility(nexto_light_tile)
                    if nexto_light_tile:
                        tile.with_light_tile = True

    def enemy_spawn(self, screen):  # спавн монстров
        if len(self.enemies_group.sprites()) == 0 and self.wave < self.waves_max and self.enemy_spawn_ability == 1:
            self.wave += 1
            self.enemy_count = 0
            self.enemy_types = self.all_enemy_types[self.wave]
            self.enemy_max_count = self.all_enemy_count[self.wave]
            self.wave_text = f'Волна №{self.wave}! \n ({", ".join(self.enemy_types)})'
            if self.enemy_types[0] in bosses:
                pygame.mixer.music.load(sounds[self.enemy_types[0]])
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.load(self.music)
                pygame.mixer.music.play()

        if self.enemy_spawn_ability and self.enemy_count < self.enemy_max_count:
            create_mob(screen, (randint(int(screen.get_width() / 2 - 41 * 25 / 2) + 50, 41 * 25), randint(int(screen.get_height() / 2 - 36 * 25 / 2) + 50, 41 * 20)), 1, self.enemy_types, self.enemies_group)
            self.enemy_count += 1
        if self.npc_spawn and len(self.npc_group.sprites()) < len(self.npc_types):
            for ind, npc in enumerate(self.npc_types):
                self.npc_group.add(NPC(self.npc_coords[ind], npc[1], npc[2], npc[0], 60))
    
    def draw_text(self, screen):
        if self.wave_text != '':
            text = self.font.render(
                    self.wave_text, 1, pygame.Color("white"))
            rect = pygame.Surface(
                (text.get_width() + 20, text.get_height() + 20))
            rect.set_alpha(128)
            rect.fill((0, 0, 0))
            screen.blit(rect, (screen.get_width() // 2 - text.get_width() - 10, screen.get_height() // 2 - text.get_height() - 10))
            screen.blit(text, (screen.get_width() // 2 - text.get_width(), screen.get_height() // 2 - text.get_height()))

    def loop(self, screen, player, fps, pos):  # цикл комнаты
        if self.wave_text != '':
            self.fps_count += 1
    
        if not self.fps_count % 100:
            self.wave_text = ''
            self.fps_count = 0
        # pygame.draw.rect(screen, pygame.Color("green"), [0, 0, screen.get_width(), screen.get_height()])
        if self.isdark:
            for tile in self.tiles:
                if not tile.with_light_tile:
                    player_visibility = player.tile_visibility(tile)
                    tile.set_visibility(player_visibility)
            for enemy in self.enemies_group:
                enemy.todark(player.tile_visibility(enemy))

        self.tiles.draw(screen)  # рисование всех тайлов
        self.light_tiles.draw(screen) # тайлы, излучающие свет
        try:
            self.enemies_group.update(player)  # цикл всех монстров
            self.enemies_group.draw(screen)  # рисование монстров
        except TypeError:
            pass # ошибка если игрок попытался нанести урон не мобам при помощи предмета
        self.npc_group.update(self.tiles)
        self.npc_group.draw(screen)
        items.Items.SPRITE_ITEMS.draw(screen)  # я сюда добавил айтемс.update
        items.Items.SPRITE_ITEMS.update(player, pos)  # я здесь добавил
        
        self.draw_text(screen)

    def clear(self):
        self.enemy_count = 0
        self.npc_count = 0
        for enemy in self.enemies_group:
            enemy.kill()
        items.Items.SPRITE_ITEMS.update(None, kill=True)

bosses = ["BOS_1", "BOS_2", "BOS_3"]

sounds = {
    "BOS_1": "sounds/bosses/boss1.mp3",
    "BOS_2": "sounds/bosses/boss2.mp3",
    "BOS_3": "sounds/bosses/boss3.mp3"
}

