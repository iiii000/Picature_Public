from enum import IntEnum
import pygame
from pygame.locals import *

from core.config import *
from data.program.enemy.enemy_factory import ENEMY_CLASS_MAP

#TODO 各子クラスへの親クラスの適応

class Enemies():
    def __init__(self, stage_data):
        self.enemies = []
        
        self.load_enemy(stage_data)

    def update(self, player_rect):
        if self.enemies == []:
            return
        for i in self.enemies:
            i.update(player_rect)
        self.delete_enemy()
        
    def draw(self, screen):
        if self.enemies == []:
            return
        for i in self.enemies:
            i.draw(screen)
    
    def move_x(self):
        for enemy in self.enemies:
            enemy.move_x()
    
    def move_y(self):
        for enemy in self.enemies:
            enemy.move_y()
    
    def collision_resolve(self):
        for enemy in self.enemies:
            enemy.collision_resolve()
        
    def delete_enemy(self):
        self.enemies = [i for i in self.enemies if i.alive]

    def load_enemy(self, data):
        for enemy_type, pos in zip(data.enemy_types, data.enemy_positions):
            enemy_cls = ENEMY_CLASS_MAP.get(enemy_type)
            self.enemies.append(enemy_cls(pos))
    
    def next_map(self, data):
        self.enemies = []
        self.load_enemy(data)

    def restart(self, stage_data):
        for enemy in self.enemies:
            enemy.restart()