import random

import pygame
from pygame.locals import *

from core.config import *

class Player():
    def __init__(self, map_data):
        self.restart_requested = False
        self.state = "idle" # "idle", "walking", "walk", "lie", "dush"

        self.frame = 0
        self.initial_position = map_data.start_position.copy()
        self.position = self.initial_position.copy()
        self.hp = PLAYER_HP
        self.speed = [0,0]

        self.images = []
        self.scarf_images = []
        self.overlay_images = []
        self.reverce_images = []
        self.reverce_scarf_images = []
        self.reverce_overlay_images = []

        self.rect = pygame.Rect(self.position[X], self.position[Y], CHARA_SIZE[X], CHARA_SIZE[Y])
        self.mask = pygame.Mask((self.rect.width, self.rect.height), fill=True)

        self.dush_speed = 75
        self.dish_distance = -1
        self.dush_length = -1
        self.dush_moved = -1
        self.attack_power = 10
        
        self.is_left = False
        self.is_ground = False
        self.is_shake = False
        self.is_event = False
        self.is_dush = False
        self.is_attacked = False
        
        self.load_image()
    
    def handle_events(self, events):
        if self.is_event:
            return
        if self.is_dush:
            return
        pressed_key = pygame.key.get_pressed()
        if pressed_key[K_a]:
            if self.state == "idle":
                self.state = "walking"
                self.frame = 0
            self.is_left = 1
            self.speed[X] = -PLAYER_MAX_SPEED[X]
        if pressed_key[K_d]:
            if self.state == "idle":
                self.state = "walking"
                self.frame = 0
            self.is_left = 0
            self.speed[X] = PLAYER_MAX_SPEED[X]
        if not pressed_key[K_a] and not pressed_key[K_d]:
            self.speed[X] = 0
            self.state = "idle"
        if pressed_key[K_SPACE] and self.is_ground:
            self.speed[Y] = -PLAYER_JUMP_POWER
            self.is_ground = False

    def update(self):
        self.frame += 1
        if self.frame == 50:
            self.frame = 0

        if self.hp <= 0:
            self.restart_requested = True
        
        if self.is_dush:
            self.update_dush()
            return

        self.speed[Y] = self.speed[Y] + PLAYER_ACC[Y]

        if self.speed[Y] > PLAYER_MAX_SPEED[Y]:
            self.speed[Y] = PLAYER_MAX_SPEED[Y]

    def draw(self, screen):
        if self.state == "idle":
            anim = 0
        elif self.state == "walking":
            anim = 1
        elif self.state == "walk":
            anim = 2
        elif self.state == "lie":
            anim = 3

        frame_index = int(self.frame / 5) % len(self.images[anim])
        scarf_frame_index = int(self.frame / 5) % len(self.scarf_images[0])

        if self.state == "walking" and frame_index == 2:
            self.state = "walk"

        if self.is_left == 0:
            image = self.images[anim][frame_index]
            overlay_image = self.overlay_images[anim][frame_index]
            scarf_image = self.scarf_images[0][scarf_frame_index]
        else:
            image = self.reverce_images[anim][frame_index]
            overlay_image = self.reverce_overlay_images[anim][frame_index]
            scarf_image = self.reverce_scarf_images[0][scarf_frame_index]

        # 👇 震え
        if self.is_shake:
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-2, 2)
        else:
            shake_x = 0
            shake_y = 0

        screen.blit(image, (self.position[0] + shake_x, self.position[1] + shake_y))
        screen.blit(scarf_image, (self.position[0] + shake_x, self.position[1] + shake_y))
        screen.blit(overlay_image, (self.position[0] + shake_x, self.position[1] + shake_y))
        #当たり判定
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
    
    def update_dush(self):
        self.dush_moved += self.dush_length
        if self.dush_moved >= self.dush_distance:
            self.is_dush = False
            self.speed = [0, 0]
    
    def dush(self, line):
        self.dish_distance = 0
        self.dush_length = 0
        self.dush_moved = 0

        self.is_ground = False
        self.is_dush = True
        self.is_attacked = False

        start = line[0]
        end = line[-1]
        
        distance = ((self.position[X] - end[X]) ** 2 + (self.position[Y] - end[Y]) ** 2) ** 0.5
        self.dush_distance = int(distance)
        self.speed[X] = int(self.dush_speed * (end[X] - start[X]) / distance)
        self.speed[Y] = int(self.dush_speed * (end[Y] - start[Y]) / distance)
        self.dush_length = int((self.speed[X] ** 2 + self.speed[Y] ** 2) ** 0.5)
    
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
    
    def collide_lines_x(self, overlap_mask, mask):
        if self.is_dush:
            return
        if self.speed[X] < 0:
            while overlap_mask.count() > 0:
                edge_x = 0
                edge_y = 0
                for x in range(overlap_mask.get_size()[X]):
                    for y in range(overlap_mask.get_size()[Y]):
                        if overlap_mask.get_at((x,y)):
                            if edge_x < x:
                                edge_x = x
                                edge_y = y
                if CHARA_SIZE[Y] - edge_y <= MAX_STEP_HEIGHT:
                    # 段差を乗り越える
                    self.rect.bottom = self.rect.y + edge_y
                    overlap_mask = self.mask.overlap_mask(mask, (-self.rect.x, -self.rect.y))
                else:
                    self.rect.left = self.rect.x + edge_x
                    self.speed[X] = 0
                    self.is_move = 0
                    break

        elif self.speed[X] > 0:
            while overlap_mask.count() > 0:
                edge_x = overlap_mask.get_size()[X]
                edge_y = 0
                for x in range(overlap_mask.get_size()[X]):
                    for y in range(overlap_mask.get_size()[Y]):
                        if overlap_mask.get_at((x,y)):
                            if edge_x > x:
                                edge_x = x
                                edge_y = y
                if CHARA_SIZE[Y] - edge_y <= MAX_STEP_HEIGHT:
                    # 段差を乗り越える
                    self.rect.bottom = self.rect.y + edge_y
                    overlap_mask = self.mask.overlap_mask(mask, (-self.rect.x, -self.rect.y))
                else:
                    self.rect.right = self.rect.x + edge_x
                    self.speed[X] = 0
                    self.is_move = 0
                    break

    def collide_map_y(self, rect):
        if self.speed[Y] > 0:
            self.rect.bottom = rect.top
            self.is_ground = 1
        elif self.speed[Y] < 0:
            self.rect.top = rect.bottom
        self.speed[Y] = 0
    
    def collide_lines_y(self, overlap_mask, mask):
        if self.is_dush:
            return
        if self.speed[Y] > 0:  # 下方向
            edge_y = self.mask.get_size()[Y]
            for x in range(self.mask.get_size()[X]):
                for y in range(self.mask.get_size()[Y]):
                    if overlap_mask.get_at((x, y)):
                        if edge_y > y:
                            edge_y = y
            self.rect.bottom = self.rect.y + edge_y
            self.is_ground = 1
            self.speed[Y] = 0
        elif self.speed[Y] < 0:  # 上方向
            edge_y = -1
            for x in range(self.mask.get_size()[X]):
                for y in range(self.mask.get_size()[Y]):
                    if overlap_mask.get_at((x, y)):
                        if edge_y < y:
                            edge_y = y
            self.rect.top = self.rect.y + edge_y + 1
            self.speed[Y] = 0
    
    def collision_resolve(self):
        self.position[X] = self.rect.x
        self.position[Y] = self.rect.y
    
    def load_image(self):
        # 色の乗算（遠景っぽく）
        #img.fill((180, 200, 255), special_flags=pygame.BLEND_RGB_MULT)

        # ぼかし追加
        #img = self.blur_surface(img, 0.5)

        #idle
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle/1.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle/2.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle/3.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle/2.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle/1.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.images.append(tmp)
        #walking
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk/1.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk/2.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk/3.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.images.append(tmp)
        #walk
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk/3.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.images.append(tmp)

        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle_scarf/1.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle_scarf/2.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle_scarf/3.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle_scarf/2.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/idle_scarf/1.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.overlay_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk_scarf/1.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk_scarf/2.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk_scarf/3.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.overlay_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/walk_scarf/3.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.overlay_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle/1.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle/2.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle/3.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle/2.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle/1.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.reverce_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk/1.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk/2.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk/3.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.reverce_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk/3.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.reverce_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle_scarf/1.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle_scarf/2.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle_scarf/3.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle_scarf/2.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/idle_scarf/1.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.reverce_overlay_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk_scarf/1.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk_scarf/2.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk_scarf/3.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.reverce_overlay_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/walk_scarf/3.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.reverce_overlay_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/scarf/1.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/scarf/2.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/scarf/3.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/scarf/4.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.transform.flip(pygame.image.load("assets/chara/scarf/5.png"), True, False), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.scarf_images.append(tmp)
        tmp=[]
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/scarf/1.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/scarf/2.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/scarf/3.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/scarf/4.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        tmp.append(pygame.transform.smoothscale(pygame.image.load("assets/chara/scarf/5.png"), (CHARA_SIZE[X], CHARA_SIZE[Y])))
        self.reverce_scarf_images.append(tmp)

        """
        self.imagelist.append(self.split_image(pygame.transform.scale2x(pygame.image.load("chara/Walk.png")),6,0))
        self.reverce_imagelist.append(self.split_image(pygame.transform.flip(pygame.transform.scale2x(pygame.image.load("chara/Idle.png")),True,False),4,1))
        self.reverce_imagelist.append(self.split_image(pygame.transform.flip(pygame.transform.scale2x(pygame.image.load("chara/Walk.png")),True,False),6,1))
        """

    def blur_surface(self, surface, scale=0.5):
        w, h = surface.get_size()
        small = pygame.transform.smoothscale(surface, (int(w * scale), int(h * scale)))
        return pygame.transform.smoothscale(small, (w, h))
    
    def damage(self, attack_power):
        self.hp -= attack_power

    def next_map(self, map_data, wall_rect):
        self.frame = 0
        self.initial_position = map_data.chara_init_pos.copy()
        self.position = self.initial_position.copy()
        
        self.speed = [0,0]
        self.rect = pygame.Rect(*self.position, *CHARA_SIZE)
        self.wall_rect = wall_rect

        self.is_left = 0
        self.is_move = 0
        self.is_ground = 0
    
    def restart(self):
        self.restart_requested = False
        self.state = "idle" # "idle", "walking", "walk", "lie"

        self.frame = 0
        self.position = self.initial_position.copy()
        self.hp = PLAYER_HP
        self.speed = [0,0]

        self.rect = pygame.Rect(self.position[X]+RECT_OFFSET/2, self.position[Y], CHARA_SIZE[X]-RECT_OFFSET, CHARA_SIZE[Y])
        self.mask = pygame.Mask((self.rect.width, self.rect.height), fill=True)

        self.is_left = False
        self.is_ground = False
        self.is_shake = False
        self.is_event = False