import pygame

from core.config import *

class Switch:
    def __init__(self, id, position):
        self.surface = pygame.Surface((VIRTUAL_WINDOW_SIZE), pygame.SRCALPHA)

        self.id = id
        self.images = []
        self.position = None
        self.rect = None
        self.state = "off" # "off" or "on" or "change"

        self.load_image()
        self.set_pos(position)
        self.create_surface()
    
    def update(self):
        pass

    
    def draw(self, screen):
        screen.blit(self.surface, (0,0))
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        
    def create_surface(self):
        self.surface.fill((0, 0, 0, 0))
        switch_image_index = 0 if self.state == "off" else 1
        self.surface.blit(self.images[switch_image_index], (self.position[X], self.position[Y]))
    
    def collide_player(self, player):
        if self.state != "on":
            self.state = "change"
        self.create_surface()
    
    def collide_magic(self, magic):
        magic.delete()
        if self.state != "on":
            self.state = "change"
        self.create_surface()
        
    
    def load_image(self):
        self.images.append(pygame.image.load("assets/gimmick/switch_off.png"))
        self.images.append(pygame.image.load("assets/gimmick/switch_on.png"))
    
    def set_pos(self, pos):
        self.position = (pos[0], pos[1])
        self.rect = self.images[0].get_rect(topleft = (self.position[X], self.position[Y]))
        self.state = "off"