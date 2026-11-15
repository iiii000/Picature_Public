from enum import Enum, auto
from pathlib import Path
import pygame
from pygame.locals import *

from core.config import *

class State(Enum):
    IDLE = auto()
    PRE_JUMP = auto()
    JUMP_START = auto()
    JUMP = auto()
    LANDING = auto()

class Rabbit():
    enemy_id = 2

    STATE_DURATION = {
        State.IDLE: 60,
        State.PRE_JUMP: 20,
        State.JUMP: 9999,
        State.LANDING: 20,
    }

    STATE_IMAGE = {
        State.IDLE: 0,       # idle画像
        State.PRE_JUMP: 0,   # しゃがみ
        State.JUMP: 0,       # 跳躍
        State.LANDING: 0,    # 着地余韻
    }

    def __init__(self, init_pos):
        self.alive = True
        self.hp = 10
        self.damage = 10

        self.imagelist = []
        self.reverce_imagelist = []
        self.rect = None
        self.bullets = []

        self.init_pos = list(init_pos)
        self.pos = list(init_pos)

        self.acc = [1,1]
        self.max_speed = [4, 60]
        self.jump_power = 15
        self.speed = [0, 0]

        self.is_right = False
        self.is_ground = True

        # 状態管理
        self.state = State.IDLE
        self.frame = 0

        self.load_image()

        # 状態更新関数
        self.state_update = {
            State.IDLE: self.update_idle,
            State.PRE_JUMP: self.update_pre_jump,
            State.JUMP: self.update_jump,
            State.LANDING: self.update_landing,
        }

    def update(self, player_pos):
        self.frame += 1
        if self.frame == 100:
            self.frame = 0
        
        self.speed[Y] += self.acc[Y]
        if self.speed[Y] > self.max_speed[Y]:
            self.speed[Y] = self.max_speed[Y]

        self.state_update[self.state](player_pos)
        
        if self.hp <= 0:
            self.delete()

        if self.bullets != []:
            for i in self.bullets:
                i.update()
            self.bullets = [i for i in self.bullets if i.alive]

    def draw(self, screen):
        image_num = self.STATE_IMAGE[self.state]

        if self.is_right:
            image = self.reverce_imagelist[image_num]
        else:
            image = self.imagelist[image_num]
        screen.blit(image, self.pos)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

        if self.bullets != []:
            for i in self.bullets:
                i.draw(screen)
    
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

    def update_idle(self, player_pos):
        if self.frame >= self.STATE_DURATION[State.IDLE]:
            self.change_state(State.PRE_JUMP)

    def update_pre_jump(self, player_pos):
        if self.frame >= self.STATE_DURATION[State.PRE_JUMP]:
            self.is_ground = 0
            self.change_state(State.JUMP)
            if self.pos[X] < player_pos[X]:
                self.speed[X] = self.max_speed[X]
                self.is_right = 1
            else:
                self.speed[X] = -self.max_speed[X]
                self.is_right = 0
            self.speed[Y] = -self.jump_power
        
    def update_jump(self, player_pos):
        if self.is_ground:
            self.speed[X] = 0
            self.speed[Y] = 0
            self.change_state(State.LANDING)
            self.bullets.append(Bullet(self.pos, 1))
            self.bullets.append(Bullet(self.pos, -1))

    def update_landing(self, player_pos):
        if self.frame >= self.STATE_DURATION[State.LANDING]:
            self.change_state(State.IDLE)

    def collide_player(self, player):
        player.damage(self.damage)
    
    def delete(self):
        self.alive = False
    
    def restart(self):
        self.alive = True
        self.hp = 10
        self.frame = 0
        self.state = State.IDLE
        self.pos = list(self.init_pos).copy()
        self.speed = [0,0]
        self.bullets = []

        self.is_move = 0
        self.is_attack = 0
    
    def load_image(self):
        enemy_name = self.__class__.__name__.lower()
        base_path = Path("assets/enemy") / enemy_name
        for state in State:
            state_name = state.name.lower()
            state_path = base_path / state_name
            images = []
            for img_path in sorted(state_path.glob("*.png")):
                img = pygame.image.load(str(img_path)).convert_alpha()
                img = pygame.transform.scale(img, ENEMY_SIZE)
                images.append(img)
            self.imagelist[state] = images
            self.reverse_imagelist[state] = [pygame.transform.flip(img, True, False) for img in images]

        self.rect = self.imagelist[State.IDLE][0].get_rect()
        self.rect.x = self.init_pos[0]
        self.rect.y = self.init_pos[1]

class Bullet():
    def __init__(self, enemy_pos, direction):
        self.alive = True
        self.damage = 10
        self.frame = 0

        self.pos = list(enemy_pos).copy()
        self.speed = 10

        self.direction = direction

        self.radius = 10
        self.rect = pygame.Rect(self.pos[X], self.pos[Y], self.radius*2, self.radius*2)
        if self.direction == 1:
            self.pos[X] += 100
        self.pos[Y] += 100 - self.radius

    def update(self):
        self.frame += 1
        self.pos[X] += self.speed * self.direction
        self.rect.center = (int(self.pos[X]), int(self.pos[Y]))
        if self.frame >= 30:
            self.delete()

    def draw(self, screen):
        pygame.draw.ellipse(screen, (255, 255, 255), self.rect)
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.radius)
        pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)
    
    def collide_player(self, player):
        self.delete()
        player.damage(self.damage)
    
    def collide_map(self):
        self.alive = False
    
    def delete(self):
        self.alive = False