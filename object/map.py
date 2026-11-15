import os
from collections import defaultdict

import pygame
from pygame.locals import *

from core.config import *

class map:
    def __init__(self, map_data, world_num, stage_num):
        self.map_data = map_data
        self.frame = 0
        self.surface_num = 0

        self.backgrounds = []
        self.platforms = []
        self.rect = []
        self.stage_surface = []

        self.load_backgrounds(world_num)
        self.load_platforms(world_num, stage_num)
        self.create_stage()
    
    def update(self):
        self.frame += 1
        if self.frame == MAP_ANIMATION_SPEED * len(self.stage_surface):
            self.frame = 0
        
        self.surface_num = int(self.frame / MAP_ANIMATION_SPEED) % len(self.stage_surface)
    
    def draw(self, screen):
        screen.blit(self.stage_surface[self.surface_num], (0, 0))
        #for i in self.rect:
            #pygame.draw.rect(screen, (255, 0, 0), i, 2)
    
    def get_layout(self, x, y):
        if x < 0 or x >= len(self.map_layout[0]) or y < 0 or y >= len(self.map_layout):
            return -1
        return self.map_layout[y][x]
    

    def load_backgrounds(self, world_num):
        self.backgrounds = []
        bg_dir = f"assets/background/{world_num}"
        if os.path.isdir(bg_dir):
            # フォルダ内のすべてのPNGファイルを読み込む
            bg_files = sorted([f for f in os.listdir(bg_dir) if f.endswith('.png')])
            for bg_file in bg_files:
                bg_path = os.path.join(bg_dir, bg_file)
                img = pygame.transform.scale(pygame.image.load(bg_path).convert_alpha(), VIRTUAL_WINDOW_SIZE)
                self.backgrounds.append(img)
    
    def load_platforms(self, world_num, stage_num):
        platform_dir = f'assets/platform/{world_num}/{stage_num}'
        if os.path.isdir(platform_dir):
            platform_files = sorted([f for f in os.listdir(platform_dir) if f.endswith('.png')])
            grouped = defaultdict(list)
            for platform_file in platform_files:
                group_num = int(platform_file.split('-')[0])
                grouped[group_num].append(platform_file)

            for group_num in sorted(grouped.keys()):
                group_imgs = []
                for i, platform_file in enumerate(grouped[group_num]):
                    platform_path = os.path.join(platform_dir, platform_file)
                    img = pygame.transform.scale(pygame.image.load(platform_path).convert_alpha(), VIRTUAL_WINDOW_SIZE)
                    group_imgs.append(img)
                    if i == 0:
                        self.rect.append(img.get_bounding_rect())
                self.platforms.append(group_imgs)

    def create_stage(self):
        background_surface = pygame.Surface(VIRTUAL_WINDOW_SIZE, pygame.SRCALPHA)
        background_surface.fill((0, 0, 0, 0))
        for i in self.map_data.backgrounds:
            background_surface.blit(self.backgrounds[i], (0, 0))
        for i in range(len(self.platforms[0])):
            stage_surface = pygame.Surface(VIRTUAL_WINDOW_SIZE, pygame.SRCALPHA)
            stage_surface.fill((0, 0, 0, 0))
            stage_surface.blit(background_surface, (0, 0))
            for j in self.platforms:
                stage_surface.blit(j[i], (0, 0))
            #pygame.draw.rect(stage_surface, (255, 0, 0), self.rect[0], 2)
            self.stage_surface.append(stage_surface)