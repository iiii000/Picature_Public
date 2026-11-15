import pygame
from pygame.locals import *

from core.config import *

class Goal():
    def __init__(self, map_data):
        self.frame = 0
        self.pos = map_data.goal_position.copy()
        self.rect = None

        self.image = None

        self.load_image()
    
    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.pos)
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


    def load_image(self):
        self.image = pygame.image.load("assets/chara/goal.png")
        self.rect = self.image.get_rect()
        self.rect.x = self.pos[X]
        self.rect.y = self.pos[Y]

    def split_image(self, image, image_num, reverse):
        imageList = []
        if reverse==1:
            for i in range(CHARA_SIZE[X]*(image_num-1), -1, -1*CHARA_SIZE[X]):
                surface = pygame.Surface((CHARA_SIZE[X],CHARA_SIZE[Y]))
                surface.blit(image, (0,0), (i,0,CHARA_SIZE[X],CHARA_SIZE[Y]))
                surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
                surface.convert()
                imageList.append(surface)
            return imageList
        
        for i in range(0, CHARA_SIZE[X]*image_num, CHARA_SIZE[X]):
            surface = pygame.Surface((CHARA_SIZE[X],CHARA_SIZE[Y]))
            surface.blit(image, (0,0), (i,0,CHARA_SIZE[X],CHARA_SIZE[Y]))
            surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
            surface.convert()
            imageList.append(surface)
        return imageList
    
    def next_map(self, map_data):
        self.frame = 0
        self.pos = map_data.goal_pos.copy()
        self.rect = pygame.Rect(*self.pos, *CHARA_SIZE)