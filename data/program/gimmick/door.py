import os
from collections import defaultdict

import pygame

from core.config import *

class Door:
    def __init__(self, id, position):
        self.surface = pygame.Surface((VIRTUAL_WINDOW_SIZE), pygame.SRCALPHA)
        
        self.id = id
        self.image = None
        self.top_image = None
        self.position = list(position)
        self.rect = None
        self.state = "close" # "close" or "pre_open" or "open"
    
        self.pre_open_time = 20
        self.frame = 0

        self.load_image()
    
    def update(self):
        if self.state == "pre_open":
            self.frame += 1
            if self.frame >= self.pre_open_time:
                self.position[X] += 1 #TODO 座標ずれ(開く前と後で画像サイズが違うため描画座標がずれてしまう)
                self.rect = self.top_image.get_rect(topleft=(self.position[X], self.position[Y]))
                self.state = "open"
    
    def draw(self, screen):
        if self.state == "close" or self.state == "pre_open":
            screen.blit(self.image, (self.position[X], self.position[Y]))
        else:
            screen.blit(self.top_image, (self.position[X], self.position[Y]))
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
    
    def collide_player(self, player):
        player.collide_map_x(self.rect)
    
    def collide_magic(self, magic):
        self.state = "pre_open"
        self.frame = 0
        magic.delete()
    
    def load_image(self):
        self.image = pygame.image.load("assets/gimmick/door/door.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 2, self.image.get_height() // 2))
        self.top_image = pygame.image.load("assets/gimmick/door/door_top.png").convert_alpha()
        self.top_image = pygame.transform.scale(self.top_image, (self.top_image.get_width() // 2, self.top_image.get_height() // 2))
        self.rect = self.image.get_rect(topleft=(self.position[X], self.position[Y]))