import pygame
import csv
from floors.floor import Floor
from floors.room import Room
from player.player import Player
from objects.object import load_image
from objects.object import Tile
import creatures.enemy
from objects.object import ALL_OBJECTS
from objects.object import Cloud
from floors.floors_settings import FSETTINGS
import sqlite3
from items import items, functions as funcs
from items.items import del_item, add_item
from gui_elements import UI_ELEMENTS


class Game:
    def __init__(self, fps=60):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.flip()
        self.fps = fps
        self.tile_size = 30

        while self.screen.get_height() // self.tile_size < 34:
            self.tile_size -= 1

        self.clock = pygame.time.Clock()
        self.running = True
        self.max_clouds = 6
        self.clouds_count = 0
        self.current_floor = 0  # на каком этаже мы находимся
        self.floor = None  # класс этажа
        self.player_group = pygame.sprite.Group()  # группа спрайтов только с игроком
        self.loading_screen = pygame.sprite.Sprite()
        self.loading_screen.image = load_image("ui/loading.png")
        self.loading_screen.image = pygame.transform.scale(self.loading_screen.image, (self.screen.get_width(), self.screen.get_height()))
        self.loading_screen.rect = self.loading_screen.image.get_rect()
        self.loading_screen.rect.x, self.loading_screen.rect.y = 0, 0
        self.screens_group = pygame.sprite.Group()
        self.screens_group.add(self.loading_screen)
        self.start = False
        self.generate_floor()  # генерация этажа
        creatures.enemy.Zombie.SPRITE_GROUP(
            creatures.enemy.Zombie, self.floor.rooms[self.floor.current_room].tiles)
        self.sounds_volume = 0
        self.player_group.add(Player(self.screen, self.fps, self.tile_size, self.sounds_volume))
        self.show_menu = False  # открыто ли меню
        self.show_inv = False  # открыт ли инвентарь
        self.main_menu_elements = pygame.sprite.Group()
        self.inventory_elements = pygame.sprite.Group()
        self.sellingmenu_elements = pygame.sprite.Group()
        self.show_sellingmenu = False
        self.clouds = pygame.sprite.Group()
        self.show_walking_guide = True
        self.arrow_group = pygame.sprite.Group()
        self.item_icon = pygame.sprite.Group()
        # группа для второстепенных ui элементов (подсказки, временные кнопки и т.п)
        self.other_ui_elements = pygame.sprite.Group()
        # тут будут кнопки, которые вне всяких меню
        self.buttons_group = pygame.sprite.Group()
        self.open_change_floor_menu = False
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        arrow = pygame.sprite.Sprite()
        arrow.image = load_image("ui/arrow.png")
        arrow.rect = arrow.image.get_rect()
        self.arrow_group.add(arrow)
        self.del_item = del_item
        self.show_fight_guide = False
        self.inventory_button = pygame.sprite.Group() # кнопки в меню инвентаря
        self.inventory_prompts = pygame.sprite.Group() # подсказки в меню инвентаря
        self.indicators = pygame.sprite.Group() # показатели игрока
        self.walking_guide()
        self.craft_cells = pygame.sprite.Group()
        self.generate_menu()
        self.market_elements = pygame.sprite.Group()
        self.show_market = False
        self.show_die_screen = False
        self.show_start_menu = False
        self.show_settings = False # настройки
        self.show_clouds = True
        self.show_prompts = True
        self.die_screen_buttons = pygame.sprite.Group() # кнопки в меню когда игрок проиграл
        self.starting_menu_elements = pygame.sprite.Group() # кнопки в начальном меню
        self.settings_elements = pygame.sprite.Group() # кнопки настроек
        self.set_settings()
        pygame.mouse.set_visible(False)
        pygame.mixer.music.load("sounds/main/main_theme.mp3")
        # pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()
    
    def set_settings(self):
        with open('settings.csv', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            result = [row for index, row in enumerate(reader)]

        self.show_clouds = result[1][0]
        self.show_prompts = result[1][1]
        self.sounds_volume = result[1][3]
        pygame.mixer.music.set_volume(float(result[1][2]))

    def read_savings(self):
        with open('savings.csv', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            result = [row for index, row in enumerate(reader)]

        return result

    def craft_item(self):
        table = [cell.item_name for cell in self.craft_cells]
        con = sqlite3.connect("items/items.sql")
        cur = con.cursor()
        result = cur.execute(f"""SELECT result FROM recipes
                    WHERE element1 = '{table[0]}' and element2 = '{table[1]}' and element3 = '{table[2]}' and element4 = '{table[3]}'""").fetchall()
        con.close()
        
        if len(result):
            add_item(result[0][0])
            for cell in self.craft_cells:
                del_item(cell.item_name)
                cell.kill()
            self.open_inv()
            self.show_inv = True

    def get_floor_id(self):
        with open('savings.csv', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            result = [row for index, row in enumerate(reader)]

        return result[1][0]

    def terminate(self):
        self.running = False
        self.start = False
    
    def open_market(self): # меню покупки
        self.show_market = not self.show_market
        self.show_inv = False
        self.show_sellingmenu = False
        self.market_elements = pygame.sprite.Group()
        con = sqlite3.connect("market/market.db")
        cur = con.cursor()
        result = cur.execute(f"""SELECT * FROM items
                    WHERE floor_id = {self.get_floor_id()}""").fetchall()
        con.close()

        x_pos, y_pos = 300, 100

        for element in result:
            self.market_elements.add(UI_ELEMENTS["marketcell"]((x_pos, y_pos), element[1], element[2], element[3]))
            x_pos += 50
            if x_pos == 600:
                x_pos = 300
                y_pos += 50


    def open_selling_menu(self):  # меню продажи товаров из инвентаря
        self.show_sellingmenu = not self.show_sellingmenu
        self.show_market = False
        self.show_inv = False
        self.sellingmenu_elements = pygame.sprite.Group()
        inv_list = funcs.list_()
        count = 0
        x_pos, y_pos = 300, 100

        for element in inv_list:
            # монеты в продаже не отображать
            if "монета" not in element[1] and "монеты" not in element[1]:
                self.sellingmenu_elements.add(UI_ELEMENTS["invbutton"](
                    (x_pos, y_pos), f"{element[1]} x{element[-2]}", element[0], element[4], None, selling=True,
                    cell_image="ui/market_button.png"))
            else:  # крестики на тех же местах, где находится предмет
                self.sellingmenu_elements.add(UI_ELEMENTS["invbutton"](
                    (x_pos, y_pos), f"**{element[1]}** Этот предмет нельзя продать!", "ui/cross_icon.png", "red", None,
                    cell_image="ui/market_button.png"))  # если предмет нельзя продать, ставим крестик!
            x_pos += 50
            count += 1
            if x_pos == 600:
                x_pos = 300
                y_pos += 50
    
    def show_equip(self): # меню экипировки
        positions = [(650, 150), (700, 100), (700, 150), (750, 150)] # расположение вех элементов
        equip_el = funcs.armor_on_hero() # экипировка, которая сейчас надета на игрока
        equip = [equip_el["weapon"], equip_el["head"], equip_el["tors"], equip_el["sheald"]]
        for index, element in enumerate(equip):
            self.inventory_elements.add(UI_ELEMENTS["invbutton"](positions[index], f"{element[1]} x{element[-2]}", element[0], element[4], None, cell_image="ui/equip_button.png"))

    def show_crafting_menu(self): # меню для крафта
        self.craft_cells = pygame.sprite.Group()
        positions = [(300, 310), (350, 310), (300, 360), (350, 360)] # расположение всех элементов

        for position in positions:
            self.craft_cells.add(UI_ELEMENTS["craftcell"](position))
        
        self.inventory_button.add(UI_ELEMENTS['button']((400, 375), 'создать', function=self.craft_item, size=(100, 30), font_size=20))

    def show_indicators(self):
        self.indicators = pygame.sprite.Group()
        indicators_pos = [((650, 225), "health"), ((700, 225), "armor"), ((750, 225), "damage")]
        
        for position in indicators_pos:
            self.indicators.add(UI_ELEMENTS["statsind"](position[0], position[1]))

    def open_inv(self):  # открыть инвентарь
        self.inventory_elements = pygame.sprite.Group()
        self.inventory_button = pygame.sprite.Group()
        self.show_inv = not self.show_inv
        self.show_market = False
        self.show_sellingmenu = False
        inventory_list = funcs.list_()
        count = 0
        x_pos, y_pos = 300, 100

        for element in inventory_list:
            self.inventory_elements.add(UI_ELEMENTS["invbutton"](
                (x_pos, y_pos), f"{element[1]} x{element[-2]}", element[0], element[4], element[-1]))
            x_pos += 50
            count += 1
            if x_pos == 600:
                x_pos = 300
                y_pos += 50

        for _ in range(24 - count):  # создание пустых клеток инвентаря
            self.inventory_elements.add(UI_ELEMENTS["invbutton"](
                (x_pos, y_pos), f"", None, None, None))
            x_pos += 50
            count += 1
            if x_pos == 600:
                x_pos = 300
                y_pos += 50
        
        self.show_equip()
        self.show_crafting_menu()
        self.show_indicators()

    def generate_menu(self):
        for el in self.main_menu_elements:
            el.kill()  # нужно, чтобы при переходе в другую комнату не накапливались кнопки друг на друге
        self.main_menu_elements.add(UI_ELEMENTS["button"](
            (100, 100), "Выйти", self.terminate))
        self.main_menu_elements.add(UI_ELEMENTS["button"](
            (100, 150), "Настройки", self.open_settings))
        self.main_menu_elements.add(UI_ELEMENTS["button"](
            (100, 200), "Инвентарь", self.open_inv))
        if self.floor.current_room == 1:
            self.main_menu_elements.add(UI_ELEMENTS["button"](
                (100, 250), "Продать", self.open_selling_menu))
            self.main_menu_elements.add(UI_ELEMENTS["button"](
                (100, 300), "Купить", self.open_market))

    def kill_prompts(self):  # очистка всего, что связано с подсказками
        for element in self.other_ui_elements:
            element.kill()  # очищаем все элементы подсказок
        for button in self.buttons_group:
            if button.type == 1:  # id кнопки подсказок - 1
                button.kill()  # убираем кнопку для завершения подсказки

    def walking_guide(self, kill=False):  # обучение как ходить
        self.other_ui_elements = pygame.sprite.Group()
        self.kill_prompts()
        self.other_ui_elements.add(
            UI_ELEMENTS["prompt"]("keyboard/w_key.png", (30, 35)))
        self.other_ui_elements.add(
            UI_ELEMENTS["prompt"]("keyboard/a_key.png", (5, 60)))
        self.buttons_group.add(UI_ELEMENTS["button"]((85, 60), "", lambda: self.walking_guide(
            kill=True), size=(25, 25), image="ui/green_button.png", type=1))
        self.other_ui_elements.add(
            UI_ELEMENTS["prompt"]("keyboard/s_key.png", (30, 60)))
        self.other_ui_elements.add(
            UI_ELEMENTS["prompt"]("keyboard/d_key.png", (55, 60)))
        if kill:
            self.show_walking_guide = False
            self.kill_prompts()

    def fight_guide(self, kill=False):  # обучение как драться
        self.other_ui_elements = pygame.sprite.Group()
        self.kill_prompts()
        self.walking_guide = False
        self.other_ui_elements.add(UI_ELEMENTS["prompt"](
            "keyboard/leftclick_mouse.png", (10, 30), size=(25, 35)))
        self.buttons_group.add(UI_ELEMENTS["button"]((45, 35), "", lambda: self.fight_guide(
            kill=True), size=(25, 25), image="ui/green_button.png", type=1))
        if kill:
            self.show_fight_guide = False
            self.kill_prompts()

    def menu(self):
        self.main_menu_elements.draw(self.screen)
        self.main_menu_elements.update(self.screen)

    def goto_another_room(self, new_room):  # В MAIN
        self.floor.rooms[self.floor.current_room].clear()
        self.floor.current_room = new_room
        creatures.enemy.Zombie.SPRITE_GROUP(
            creatures.enemy.Zombie, self.floor.rooms[self.floor.current_room].tiles)

    def generate_floor(self):  # генерация этажа и создание всех комнат в нём
        self.screens_group.draw(self.screen)
        self.current_floor = int(self.get_floor_id())

        con = sqlite3.connect("player/player.sql")
        cur = con.cursor()
        result = cur.execute(f"""SELECT status FROM opened_floors WHERE floor_id = {self.current_floor + 1}""").fetchall()
        con.close()

        # 0 - подземелье, 1 - рынок, 2- главная площадь, 3 - фарм зона
        self.floor = Floor([Room(FSETTINGS[self.current_floor][0]),
                            Room(FSETTINGS[self.current_floor][1]),
                            Room(FSETTINGS[self.current_floor][2]),
                            Room(FSETTINGS[self.current_floor][3])])
        self.floor.rooms[2].show_door_up = int(result[0][0])
        # генерация всех комнат в этаже
        self.floor.generate_rooms(ALL_OBJECTS, self.screen, self.tile_size)
        self.screens_group = pygame.sprite.Group()

    def move_arrow(self):
        self.arrow_group.sprites()[0].rect.x = pygame.mouse.get_pos()[0]
        self.arrow_group.sprites()[0].rect.y = pygame.mouse.get_pos()[1]
    
    def spawn_player(self):
        self.floor.current_room = 2
        self.player_group.sprites()[0].rect.x, self.player_group.sprites()[0].rect.y = self.screen.get_width() / 2 - 41 * self.tile_size / 2 + 100, self.screen.get_height() / 2 - 36 * self.tile_size / 2 + 13 * self.tile_size
        self.show_die_screen = False
        self.player_group.sprites()[0].health += 20
        self.screens_group = pygame.sprite.Group()
        self.die_screen_buttons = pygame.sprite.Group()

    def die_screen(self):
        self.screens_group.draw(self.screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEMOTION:
                self.move_arrow()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.die_screen_buttons:
                        button.onclick()
        self.die_screen_buttons.draw(self.screen)
        self.die_screen_buttons.update(self.screen)
        font = pygame.font.SysFont('Comic Sans MS', 30)
        text = font.render(
            "Вы были убиты", 1, pygame.Color("white"))
        rect = pygame.Surface(
            (text.get_width() + 10, text.get_height() + 5))
        rect.set_alpha(128)
        rect.fill((0, 0, 0))
        self.screen.blit(rect, (self.screen.get_width() // 2 - text.get_width() // 2 - 5, self.screen.get_height() // 2 - 255))
        self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, self.screen.get_height() // 2 - 250))
        self.arrow_group.draw(self.screen)
    
    def start_game(self):
        self.start = True
        self.screens_group = pygame.sprite.Group()
        self.starting_menu_elements = pygame.sprite.Group()

    def get_settings(self):
        with open('settings.csv', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            result = [row for index, row in enumerate(reader)]

        return result
    
    def write_settings(self, settings):
        with open('settings.csv', 'w', newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in settings:
                writer.writerow(row)
    
    def change_settings(self, clouds=None, prompts=None, music_load=None, sounds_load=None):
        print(clouds)
        settings = self.get_settings()
        if clouds == 1 or clouds == 0:
            settings[1][0] = clouds
            self.show_clouds = clouds
        if prompts == 1 or prompts == 0:
            settings[1][1] = prompts
            self.show_prompts = prompts
        if music_load is not None:
            settings[1][2] = music_load
            pygame.mixer.music.set_volume(music_load)
        if sounds_load is not None:
            settings[1][3] = sounds_load
            self.sounds_volume = sounds_load
        self.write_settings(settings)
        self.open_settings()
        self.show_settings = True
        

    def open_settings(self):
        self.show_settings = not self.show_settings
        self.settings_elements = pygame.sprite.Group()
        settings = self.get_settings()
        if int(settings[1][0]):
            self.settings_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 200), "Отключить облака", lambda: self.change_settings(clouds=0), font_size=18))
        else:
            self.settings_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 200), "Включить облака", lambda: self.change_settings(clouds=1), font_size=18))

        if int(settings[1][1]):
            self.settings_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 150), "Отключить подсказки", lambda: self.change_settings(prompts=0), font_size=15))
        else:
            self.settings_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 150), "Включить подсказки", lambda: self.change_settings(prompts=1), font_size=15))
        
        self.settings_elements.add(UI_ELEMENTS["valuecontroller"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 100), "Громкость музыки:",  float(settings[1][2]), lambda value: self.change_settings(music_load=value), 0, 1, 0.10, percent=True))
        self.settings_elements.add(UI_ELEMENTS["valuecontroller"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 50), "Громкость звуков:",  float(settings[1][3]), lambda value: self.change_settings(sounds_load=value), 0, 1, 0.10, percent=True))
        
        self.settings_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2), "Назад", self.open_settings))

    def run(self):
        self.screens_group.add(self.loading_screen)
        self.starting_menu_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 200), "Начать игру", self.start_game))
        self.starting_menu_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 150), "Настройки", self.open_settings))
        self.starting_menu_elements.add(UI_ELEMENTS["button"]((self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 100), "Выход", self.terminate))
        
        while not self.start:
            self.screens_group.draw(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                if event.type == pygame.MOUSEMOTION:
                    self.move_arrow()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.show_settings:
                            for button in self.starting_menu_elements:
                                button.onclick()
                        else:
                            for button in self.settings_elements:
                                button.onclick()
            
            if not self.show_settings:
                self.starting_menu_elements.draw(self.screen)
                self.starting_menu_elements.update(self.screen)
            else:
                self.settings_elements.draw(self.screen)
                self.settings_elements.update(self.screen)

            if not self.running:
                break

            font = pygame.font.SysFont('Comic Sans MS', 30)
            text = font.render(
                "Caves and Monsters", 1, pygame.Color("white"))
            rect = pygame.Surface(
                (text.get_width() + 10, text.get_height() + 5))
            rect.set_alpha(128)
            rect.fill((0, 0, 0))
            self.screen.blit(rect, (self.screen.get_width() // 2 - text.get_width() // 2 - 5, self.screen.get_height() // 2 - 255))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, self.screen.get_height() // 2 - 250))

            self.arrow_group.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(self.fps)

        while self.running:
            if not self.show_die_screen:
                pos = None
                if not self.floor.rooms[self.floor.current_room].isdark:
                    self.screen.fill(pygame.Color("skyblue"))
                else:
                    self.screen.fill(pygame.Color("black"))
                if self.clouds_count < self.max_clouds:
                    self.clouds.add(
                        Cloud((self.screen.get_width(), self.screen.get_height())))
                    self.clouds_count += 1
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for button in self.buttons_group:
                                button.onclick()
                            pos = event.pos

                            # --------------------- атака ----------------------------
                            # атака врагов:
                            self.player_group.sprites()[0].attack(
                                self.floor.rooms[self.floor.current_room].enemies_group.sprites(), event.pos)

                            # --------------------------------------------------------

                            if self.show_menu:
                                for element in self.main_menu_elements:
                                    element.onclick()
                                if self.show_inv:
                                    for button in self.inventory_button:
                                        button.onclick()
                                    for element in self.inventory_elements:
                                        element.onclick(
                                            self.player_group.sprites()[0], self)
                                if self.show_sellingmenu:
                                    for element in self.sellingmenu_elements:
                                        element.onclick(
                                            self.player_group.sprites()[0], self)
                                if self.show_market:
                                    for el in self.market_elements:
                                        el.onclick(self.player_group.sprites()[0], self)
                                if self.show_settings:
                                    for el in self.settings_elements:
                                        el.onclick()
                        elif event.button == 3: # right click
                            if self.show_inv:
                                for element in self.inventory_elements:
                                        element.right_click(self.craft_cells, self.inventory_elements)
                                
                                for element in self.craft_cells:
                                    element.right_click(self.inventory_elements)

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:  # на esc открывать меню
                            self.show_menu = not self.show_menu
                            self.show_inv = False
                            self.show_sellingmenu = False
                        if event.key == pygame.K_f: # test
                            self.player_group.sprites()[-1].freeze()
                        
                    if event.type == pygame.MOUSEMOTION:
                        self.move_arrow()

                self.floor.rooms[self.floor.current_room].enemy_spawn(
                    self.screen)  # спавн монстров в комнате
                self.floor.loop(self.screen, self.player_group.sprites()[
                    0], self.fps, pos)  # цикл этажа

                self.player_group.update(
                    self.floor.rooms[self.floor.current_room].tiles, self)  # цикл игрока
                self.player_group.draw(self.screen)  # рисование игрока
                if not self.floor.rooms[self.floor.current_room].isdark and self.show_clouds:
                    self.clouds.update()
                    self.clouds.draw(self.screen)

                if self.show_prompts:
                    self.buttons_group.update(self.screen)
                    self.buttons_group.draw(self.screen)
                    self.other_ui_elements.update()
                    self.other_ui_elements.draw(self.screen)

                if self.show_walking_guide and self.show_prompts:  # тут надпись для обученя ъодьбы
                    text = self.font.render(
                        "Чтобы перемещаться, используйте", 1, pygame.Color("white"))
                    rect = pygame.Surface(
                        (text.get_width() + 10, text.get_height() + 5))
                    rect.set_alpha(128)
                    rect.fill((0, 0, 0))
                    self.screen.blit(rect, (5, 5))
                    self.screen.blit(text, (10, 5))

                if self.show_fight_guide and self.show_prompts:  # надпись для обучения как драться
                    text = self.font.render(
                        "Чтобы атаковать, наведитесь на врага, находящегося в вашем круге атаки и нажмите", 1,
                        pygame.Color("white"))
                    rect = pygame.Surface(
                        (text.get_width() + 10, text.get_height() + 5))
                    rect.set_alpha(128)
                    rect.fill((0, 0, 0))
                    self.screen.blit(rect, (5, 5))
                    self.screen.blit(text, (10, 5))

                if self.show_menu:
                    self.menu()

                if self.show_inv:
                    self.inventory_elements.draw(self.screen)
                    self.inventory_elements.update(self.screen)
                    self.craft_cells.draw(self.screen)
                    self.craft_cells.update(self.screen)
                    self.inventory_button.draw(self.screen)
                    self.inventory_button.update(self.screen)
                    self.indicators.update(self.player_group.sprites()[0], self.screen)
                    self.indicators.draw(self.screen)

                if self.show_sellingmenu:
                    self.sellingmenu_elements.draw(self.screen)
                    self.sellingmenu_elements.update(self.screen)
                
                if self.show_market:
                    self.market_elements.draw(self.screen)
                    self.market_elements.update(self.screen)

                if self.open_change_floor_menu:
                    self.change_floor_menu_elements.draw(self.screen)
                
                if self.show_settings:
                    self.settings_elements.draw(self.screen)
                    self.settings_elements.update(self.screen)

                if len(self.screens_group.sprites()):
                    self.screens_group.draw(self.screen)

                self.arrow_group.draw(self.screen)
            else:
                self.die_screen()
            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()


if __name__ == "__main__":
    game = Game(60)
    print(game.screen.get_height())
    game.run()


rooms = ["Подземелье", "Рынок", "Главная площадь", "Пещеры"]

