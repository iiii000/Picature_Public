from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
import pygame
from pygame.locals import *

from core.config import *

class Enemy(ABC):
    enemy_id = -1
    def __init__(self, pos):
        self.init_pos = list(pos)
        self.pos = list(pos)
        self.alive = True

    def __init__(self, pos):
        pass
    
    @abstractmethod
    def update(self, player_rect):
        pass
    
    @abstractmethod
    def draw(self, screen):
        pass
    
    def move_x(self):
        self.rect.x += self.speed[X]
    
    def move_y(self):
        self.rect.y += self.speed[Y]
    
    def collide_map_x(self, rect):
        if self.speed[X] > 0:
            self.rect.right = rect.left
        elif self.speed[X] < 0:
            self.rect.left = rect.right
        self.speed[X] = 0
        self.is_move = 0
    
    def collide_map_y(self, rect):
        if self.speed[Y] > 0:
            self.rect.bottom = rect.top
            self.is_ground = 1
        elif self.speed[Y] < 0:
            self.rect.top = rect.bottom
        self.speed[Y] = 0
    
    def collision_resolve(self):
        self.pos[X] = self.rect.x
        self.pos[Y] = self.rect.y
    
    def change_state(self, new_state):
        """状態変更"""
        self.state = new_state
        self.frame = 0

    def collide_player(self, player):
        player.damage(self.damage)
    
    def damage(self, attack_power):
        self.hp -= attack_power

    def delete(self):
        self.alive = False
    
    @abstractmethod
    def restart(self):
        pass