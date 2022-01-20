import pygame
from objects.object import load_image
from objects.object import COLLIDE_OBJECTS
from objects.object import ALL_FUNCTIONAL
from items.items import buy_object
from items import functions as funcs
from random import randint


class Button(pygame.sprite.Sprite):
    def __init__(self, position, text, function, size=None, image="button.png", type=0, font_size=30, *groups):
        super().__init__(*groups)
        self.image = load_image(image)
        if size is not None:
            self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.text = text
        self.type = type
        self.function = function
        self.collide_sound = pygame.mixer.Sound("sounds/interface/collide.ogg")
        self.font = pygame.font.SysFont('Comic Sans MS', font_size)
    
    def update(self, screen):
        textsurface = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(textsurface, (self.rect.x + 10, self.rect.y))

    def onclick(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.collide_sound.play()
            self.function()


class ValueController(pygame.sprite.Sprite):
    def __init__(self, position, text, value, function, min_value, max_value, step, percent=False, *group):
        super().__init__(*group)
        self.image = load_image("button.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.plus_button = pygame.sprite.Sprite()
        self.minus_button = pygame.sprite.Sprite()
        self.ok_button = pygame.sprite.Sprite()
        self.plus_button.image = load_image("ui/inv_button.png")
        self.plus_button.image = pygame.transform.scale(self.plus_button.image, (50, 50))
        self.plus_button.rect = self.plus_button.image.get_rect()
        self.plus_button.rect.x, self.plus_button.rect.y = position[0] + self.image.get_width() + 5, position[1]
        self.minus_button.image = load_image("ui/inv_button.png")
        self.minus_button.image = pygame.transform.scale(self.minus_button.image, (50, 50))
        self.minus_button.rect = self.minus_button.image.get_rect()
        self.minus_button.rect.x, self.minus_button.rect.y = position[0] - 55, position[1]
        self.ok_button.image = load_image("ui/inv_button.png")
        self.ok_button.image = pygame.transform.scale(self.ok_button.image, (50, 50))
        self.ok_button.rect = self.ok_button.image.get_rect()
        self.ok_button.rect.x, self.ok_button.rect.y = position[0] + self.image.get_width() + 60, position[1]
        self.value = value
        self.max_value = max_value
        self.min_value = min_value
        self.function = function
        self.percent = percent
        self.text = text
        self.body = pygame.sprite.Group()
        self.body.add(self.plus_button)
        self.body.add(self.minus_button)
        self.body.add(self.ok_button)
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.step = step
    
    def onclick(self):
        if self.plus_button.rect.collidepoint(pygame.mouse.get_pos()):
            if self.value < self.max_value:
                self.value += self.step
                self.value = round(self.value, 1)
        if self.minus_button.rect.collidepoint(pygame.mouse.get_pos()):
            if self.value > self.min_value:
                self.value -= self.step
                self.value = round(self.value, 1)
        if self.ok_button.rect.collidepoint(pygame.mouse.get_pos()):
            self.function(self.value)
    
    def update(self, screen):
        self.body.draw(screen)
        value = self.value
        if self.percent:
            value = f"{int(self.value * 100)}%"
        text_plus = self.font.render("+", 1, pygame.Color("green"))
        screen.blit(text_plus, (self.plus_button.rect.x + 18, self.plus_button.rect.y))
        text_minus = self.font.render("-", 1, pygame.Color("red"))
        screen.blit(text_minus, (self.minus_button.rect.x + 18, self.minus_button.rect.y))
        text_ok = self.font.render("ok", 1, pygame.Color("white"))
        screen.blit(text_ok, (self.ok_button.rect.x + 10, self.ok_button.rect.y))
        font = pygame.font.SysFont('Comic Sans MS', 15)
        text_main = font.render(f"{self.text} {value}", 1, pygame.Color("black"))
        screen.blit(text_main, (self.rect.x + 10, self.rect.y))


class StatsIndicator(pygame.sprite.Sprite):
    def __init__(self, position, stat_type, *group):
        super().__init__(*group)
        self.image = load_image(STATS_ICONS[stat_type][0])
        self.get_text = STATS_ICONS[stat_type][1]
        self.image = pygame.transform.scale(self.image, (30, 28))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.font = pygame.font.SysFont('Comic Sans MS', 10)
        self.cell_group = pygame.sprite.Group()
        cell = pygame.sprite.Sprite()
        cell.image = load_image("ui/stats_button.png")
        cell.rect = cell.image.get_rect()
        cell.rect.x = self.rect.x
        cell.rect.y = self.rect.y
        self.rect.x += 8
        self.rect.y += 8
        self.cell_group.add(cell)
    
    def update(self, player, screen):
        self.cell_group.draw(screen)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            text = self.font.render(
                self.get_text(player), 1, pygame.Color("white"))
            rect = pygame.Surface(
                (text.get_width() + 10, text.get_height() + 5))
            rect.set_alpha(128)
            rect.fill((0, 0, 0))
            screen.blit(rect, (self.rect.x - 5, self.rect.y - 20))
            screen.blit(text, (self.rect.x, self.rect.y - 20))


class NPC(pygame.sprite.Sprite):
    def __init__(self, position, r, text, sheet, game_fps, *group):
        super().__init__(*group)
        self.frames = [self.cut_sheet(load_image(f"{sheet}/walk_up.png"), 9, 1, 64, (33, 50)),
                       self.cut_sheet(load_image(f"{sheet}/walk_down.png"), 9, 1, 64, (33, 50)),
                       self.cut_sheet(load_image(f"{sheet}/walk_left.png"), 9, 1, 63.9, (27, 50)),
                       self.cut_sheet(load_image(f"{sheet}/walk_right.png"), 9, 1, 63.9, (27, 50))] 
        self.image = self.frames[0][0]
        self.rect = self.image.get_rect()
        self.sheet = sheet
        self.rect.x, self.rect.y = position
        self.center = position
        self.current_anim = 0
        self.current_frame = 0
        self.rest_image = load_image(f"{sheet}/rest.png")  # стоит на месте
        self.direction = [0, 0]
        self.R = r
        self.R_moved = 0
        self.speed = 50 / game_fps
        self.fps_count = 0
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows, n,
                  size):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        result = list()
        frame_location = 0  

        for _ in range(columns):
            result.append(sheet.subsurface(pygame.Rect(
                (frame_location, 0),
                size)))
            frame_location += n

        return result
    
    def anim(self):
        self.image = self.frames[self.current_anim][self.current_frame]
        if self.current_frame < len(self.frames[self.current_anim]) - 1:
            self.current_frame += 1
        elif self.current_frame == len(self.frames[self.current_anim]) - 1:
            self.current_anim = 0
    
    def change_direction(self):
        new_direction = [randint(-1, 1), randint(-1, 1)]
        while self.direction[0] == new_direction[0] and self.direction[1] == new_direction[1]:
            new_direction = [randint(-1, 1), randint(-1, 1)]
        self.direction = new_direction
        if self.direction[0] < 0:
            self.current_anim = 2
        elif self.direction[0] > 0:
            self.current_anim = 3
        elif self.direction[1] < 0:
            self.current_anim = 0
        elif self.direction[1] > 0:
            self.current_anim = 1
        self.current_frame = 0
        self.R_moved = 0
    
    def collider(self, tiles):
        for tile in tiles:
            if pygame.sprite.collide_mask(self, tile) and tile.id in COLLIDE_OBJECTS and tile.id not in ALL_FUNCTIONAL:
                if self.direction[0]:
                    self.rect.x -= 1
                else:
                    self.rect.x += 1
                if self.direction[1]:
                    self.rect.y -= 1
                else:
                    self.rect.y += 1
                self.change_direction()
    
    def move(self):
        if self.R > self.R_moved and self.direction[0] and self.direction[1]:
            self.rect.x += self.direction[0] * self.speed
            self.rect.y += self.direction[1] * self.speed
            self.R_moved += self.speed
            self.anim()
        elif self.R <= self.R_moved:
            self.image = self.rest_image
        
        if (self.rect.x - self.center[0]) ** 2 + (self.rect.y - self.center[1]) ** 2 > self.R ** 2:
            if self.rect.x < self.center[0]:
                self.direction[0] = 1
                self.direction[0] += self.speed
                self.current_anim = 3
            else:
                self.direction[0] = -1
                self.direction[0] -= self.speed
                self.current_anim = 2
            if self.rect.y < self.center[1]:
                self.direction[1] = 1
                self.direction[1] += self.speed
                self.current_anim = 1
            else:
                self.direction[1] = -1
                self.direction[1] -= self.speed
                self.current_anim = 0
            self.R_moved = 0
            self.anim()
    
    def update(self, tiles):
        self.fps_count += 1
        if not self.fps_count % 20:
            if randint(0, 1):
                self.direction = [0, 0]
                self.image = self.rest_image
            else:
                self.change_direction()
        
        if not self.fps_count % 2:
            self.move()


class CraftCell(pygame.sprite.Sprite):
    def __init__(self, position, image="inv_button.png", *group):
        super().__init__(*group)
        self.image = load_image(f"ui/{image}")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.item_icon = pygame.sprite.Group()
        self.item_name = "" # пусто так как в рецепте может быть пустая клетка
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        self.collide_sound = pygame.mixer.Sound("sounds/interface/put.ogg")
        self.delete_sound = pygame.mixer.Sound("sounds/interface/unput.ogg")
    
    def put_item(self, item_name, icon_image): # добавление элемента на ячейку крафта
        self.collide_sound.play()
        self.icon = pygame.sprite.Sprite()
        self.icon.image = load_image(icon_image)
        self.icon.image = pygame.transform.scale(self.icon.image, (25, 25))
        self.icon.rect = self.icon.image.get_rect()
        self.icon.rect.x = self.rect.x + 10
        self.icon.rect.y = self.rect.y + 10
        self.item_icon.add(self.icon)
        self.item_name = item_name
    
    def right_click(self, inv_group): # действия если нажата правая кнопка мыши 
        self.delete_sound.play()
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.item_icon = pygame.sprite.Group() # очищение картинки предмета
            for element in inv_group:
                if element.text.split(" x")[0] == self.item_name and element.hide:
                    element.hide = False
                    break
            self.item_name = ""
    
    def update(self, screen):
        if len(self.item_icon.sprites()):
            self.item_icon.draw(screen)
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                textsurface = self.font.render(self.item_name, True, pygame.Color("White"))
                screen.blit(textsurface, (self.rect.x, self.rect.y - 20))


class Sign(pygame.sprite.Sprite):
    def __init__(self, position, text, *group):
        super().__init__(*group)
        self.image = load_image("sign.png")
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        self.text = text
    
    def update(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            text = self.font.render(
                self.text, 1, pygame.Color("white"))
            rect = pygame.Surface(
                (text.get_width() + 10, text.get_height() + 5))
            rect.set_alpha(128)
            rect.fill((0, 0, 0))
            screen.blit(rect, (self.rect.x - 5, self.rect.y - 20))
            screen.blit(text, (self.rect.x, self.rect.y - 20))


class Prompt(pygame.sprite.Sprite):
    def __init__(self, image, position, size=(25, 25), *group):
        super().__init__(*group)
        self.image = load_image(f"ui/{image}")
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.fps_count = 0

class MarketCell(pygame.sprite.Sprite):
    def __init__(self, position, text, price, image, cell_image="ui/market_button.png", *groups):
        super().__init__(*groups)
        self.image = load_image(cell_image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.text = text
        self.icon_image = image
        self.price = price
        if self.icon_image is not None:
            self.item_icon = pygame.sprite.Group()
            icon = pygame.sprite.Sprite()
            icon.image = load_image(self.icon_image)
            icon.image = pygame.transform.scale(icon.image, (25, 25))
            icon.rect = icon.image.get_rect()
            icon.rect.x = self.rect.x + 10
            icon.rect.y = self.rect.y + 10
            self.item_icon.add(icon)
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
    
    def update(self, screen):
        if self.icon_image is not None:
            self.item_icon.draw(screen)
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                textsurface = self.font.render(f"{self.text} | {self.price} медных монет", True, pygame.Color("White"))
                screen.blit(textsurface, (self.rect.x, self.rect.y - 20))
    
    def onclick(self, player, game):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            buy_object(self.text, price=self.price)
            game.open_market()
            game.show_market = True


class InventoryButton(pygame.sprite.Sprite):
    def __init__(self, position, text, image, color, function, cell_image="ui/inv_button.png", selling=False, *groups):
        super().__init__(*groups)
        self.image = load_image(cell_image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.text = text
        self.color = color
        self.icon_image = image
        self.selling = selling
        self.hide = False # нужно, чтобы можно было прятать если для крафта использовано больше чем колд-во
        if self.icon_image is not None:
            self.item_icon = pygame.sprite.Group()
            icon = pygame.sprite.Sprite()
            icon.image = load_image(self.icon_image)
            icon.image = pygame.transform.scale(icon.image, (25, 25))
            icon.rect = icon.image.get_rect()
            icon.rect.x = self.rect.x + 10
            icon.rect.y = self.rect.y + 10
            self.item_icon.add(icon)
        self.function = function
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
    
    def update(self, screen):
        if self.icon_image is not None and not self.hide:
            self.item_icon.draw(screen)
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                textsurface = self.font.render(self.text, True, pygame.Color(self.color))
                screen.blit(textsurface, (self.rect.x, self.rect.y - 20))
    
    def onclick(self, player, game):
        if self.function is not None and not self.hide:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.function(hero=player, game=game, index=self.text.split(' x')[0])
                game.open_inv()
                game.show_inv = True
                player.update_stats()
        else:
            if self.selling and self.rect.collidepoint(pygame.mouse.get_pos()):
                print(self.text)
                funcs.traiding_to_money(self.text.split(' x')[0])
                game.open_selling_menu()
                game.show_sellingmenu = True
    
    def right_click(self, craft_group, inv_group):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            elements = list()
            self_count = 0
            for el in inv_group: # подсчет общего кол-ва предмета из всех ячеек инвентаря
                if el.text.split(' x')[0] == self.text.split(' x')[0]:
                    self_count += int(el.text.split(' x')[1])

            for element in craft_group:
                elements.append(element.item_name)
                if element.item_name == "" and self.icon_image and elements.count(self.text.split(' x')[0]) + 1 <= self_count:
                    element.put_item(self.text.split(' x')[0], self.icon_image)
                    if elements.count(self.text.split(' x')[0]) + 1 >= int(self.text.split(' x')[1]):
                        self.hide = True
                    return 1



UI_ELEMENTS = {
    "button": Button,
    "invbutton": InventoryButton,
    "prompt": Prompt,
    "marketcell": MarketCell,
    "craftcell": CraftCell,
    "statsind": StatsIndicator,
    "valuecontroller": ValueController
}

STATS_ICONS = {
    "health": ("ui/health_stats.png", lambda player: f"{player.health}/{player.max_health}"),
    "armor": ("ui/kd_stats.png", lambda player: f"{player.armor} armor"),
    "damage": ("ui/damage_stats.png", lambda player: f"{player.damage} damage/click")
}

