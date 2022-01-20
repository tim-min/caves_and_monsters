import pygame
import os
import sys
from random import randint, randrange


def load_image(name, colorkey=None):
    fullname = os.path.join('assets', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image

class Cloud(pygame.sprite.Sprite):
    def __init__(self, screen_size, *groups):
        super().__init__(*groups)
        self.image = load_image(f"bg/cloud{randint(1, 8)}.png")
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.screen_size = screen_size
        self.rect.x, self.rect.y = randint(0, screen_size[0] // 2), randint(0, screen_size[1])
    
    def update(self):
        self.rect.x += 1
        if self.rect.x > self.screen_size[0]:
            self.rect.x = randint(-500, -160)
            self.rect.y = randint(0, self.screen_size[1])



class Tile(pygame.sprite.Sprite):
    def __init__(self, path, id, coords, size, *group, collide_func=None):
        super().__init__(*group)
        self.image = load_image(path)
        self.image = pygame.transform.scale(self.image, (size, size))
        self.size = size
        self.id = id
        self.collide_function = collide_func
        self.path = path
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coords
        self.indark = False
        self.with_light_tile = False # находится ли источник света рядом с этим тайлом (нужно для оптимизации)
    
    def set_visibility(self, visibility):
        if not self.with_light_tile:
            if not visibility and not self.indark:
                self.image = load_image("dark_tile.png")
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
                self.indark = True
            elif visibility and self.indark:
                self.image = load_image(self.path)
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
                self.indark = False
    
    def in_radius(self, other):
        if (other.rect.x - self.rect.x) ** 2 + (other.rect.y - self.rect.y) ** 2 <= 100 ** 2:
            return True
        return False

ALL_OBJECTS = [("grass_tile.png", 0), ("rock_tile.png", 1), ("dirt_tile.png", 2), ("TradeHouse1_tile.png", 3), ("TradeHouse2_tile.png", 4), ("TradeHouse3_tile.png", 5), ("TradeHouse4_tile.png", 6), ("hor_rails_tile.png", 7), ("tree_tile.png", 8),
               ("fence_tile.png", 9), ("fence_vert_tile.png", 10), ("flowers1_tile.png", 11), ("flowers2_tile.png", 12), ("flowers3_tile.png", 13), ("flowers4_tile.png", 14), ("lifeWall_tile.png", 15), ("lifeWallVert_tile.png", 16),
               ("lake1_tile.png", 17), ("lake2_tile.png", 18), ("lake3_tile.png", 19), ("lake4_tile.png", 20), ("water_tile.png", 21), ("lake5_tile.png", 22), ("lake6_tile.png", 23), ("lake7_tile.png", 24), ("lake8_tile.png", 25), ("campfire_tile.png", 26), ("door_tile.png", 27),
               ("torch_tile.png", 28), ("door2_tile.png", 29), ("tradestall1_tile.png", 30), ("tradestall2_tile.png", 31), ("lane_tile.png", 32), ("spruce_tile.png", 33), ("tent_1.png", 34), ("tent_2.png", 35), ("tent_3.png", 36), ("tent_4.png", 37), ("stump_axe.png", 38), ("gate_tile.png", 39),
               ("fence_left_tile.png", 40), ("fence_right_tile.png", 41), ("stump_block_tile.png", 42), ("circle_road_tile.png", 43), ("grass_object.png", 44), ("snow_tile.png", 45), ("wintered_spruce.png", 46), ("present_box_tile.png", 47), ("ruins_fence.png", 48), ("ruins_fence2.png", 49), ("fence_tile2.png", 50),
               ("old_campfire_tile.png", 51), ("barrel_object.png", 52), ("ice_tile.png", 53), ("chest_tile.png", 54), ("tombstone_tile.png", 55), ("cross_tile.png", 56), ("stone_tile.png", 57), ("door_floor_up.png", 58), ("door_floor_down.png", 59)]
COLLIDE_OBJECTS = [1, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59] # тайлы, через которые нельзя пройти

 # объекты, которые делают что-то (пример: ускорение когда игрок идёт по дорожке)
FUNCTIONAL_OBJECTS = {
    "ACCELERATION": [32, 43, 53],
    "GATE": [39],
    "LIGHT": [28],
    "FLOORCHANGE_UP": [58],
    "FLOORCHANGE_DOWN": [59]
}
ALL_FUNCTIONAL = [32, 43, 39, 53, 28, 58, 59]
TRANSPARENT_OBJECTS = ['3', '4', '5', '6', '7', "8", "9", "10", "11", "12", "13", "14", "15", "16", "26", "28", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "46", "47", "48", "49", "50", "51", "52", "54", "55", "56", "58", "59"] # прозрачные тайлы
