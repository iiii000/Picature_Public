from enum import Enum, auto
from pathlib import Path
import pygame
from pygame.locals import *

from core.config import *
from .enemy_base import Enemy

class State(Enum):
    IDLE = auto()
    MOVE = auto()
    WAIT = auto()

class Invy(Enemy):
    enemy_id = 4
    
    STATE_DURATION = {
        State.IDLE: 10,
        State.MOVE: 180,
        State.WAIT: 60,
    }

    STATE_IMAGE = {
        State.IDLE: 0,       # idle画像
        State.MOVE: 0,   # しゃがみ
        State.WAIT: 0,    # 着地余韻
    }

    def __init__(self, init_pos):
        self.alive = True
        self.hp = 10
        self.damage = 10
        self.search_range = 100
        self.attack_range = 5

        self.imagelist = {
            State.IDLE: [],
            State.MOVE: [],
            State.WAIT: [],
        }

        self.reverse_imagelist = {
            State.IDLE: [],
            State.MOVE: [],
            State.WAIT: [],
        }

        self.rect = None
        self.bullets = []

        self.init_pos = list(init_pos[0])
        self.pos = list(init_pos[0])
        self.move_pos = list(init_pos[1:])

        self.acc = [1,1]
        self.max_speed = [1, 1]
        self.jump_power = 0
        self.speed = [0, 0]

        self.is_attack = False
        self.is_right = False

        # 状態管理
        self.state = State.IDLE
        self.frame = 0

        self.load_image()

        # 状態更新関数
        self.state_update = {
            State.IDLE: self.update_idle,
            State.MOVE: self.update_move,
            State.WAIT: self.update_wait,
        }

    def update(self, player_pos):
        self.frame += 1
        if self.frame == 100 * ENEMY_ANIMATION_SPEED * len(self.imagelist[self.state]):
            self.frame = 0

        self.state_update[self.state](player_pos)
        
        if self.hp <= 0:
            self.delete()

        if self.bullets != []:
            for i in self.bullets:
                i.update()
            self.bullets = [i for i in self.bullets if i.alive]

    def draw(self, screen):
        image_num = int(self.frame/ENEMY_ANIMATION_SPEED) % len(self.imagelist[self.state])

        if self.is_right:
            image = self.reverce_imagelist[self.state][image_num]
        else:
            image = self.imagelist[self.state][image_num]
        screen.blit(image, self.pos)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

        if self.bullets != []:
            for i in self.bullets:
                i.draw(screen)

    def update_idle(self, player_pos):
        if self.frame >= self.STATE_DURATION[State.IDLE]:
            self.change_state(State.MOVE)

    def update_move(self, player_pos):
        if self.pos[X] < player_pos[X]:
            self.speed[X] += self.acc[X]
            if(self.speed[X]>=self.max_speed[X]):
                self.speed[X]=self.max_speed[X]
        elif self.pos[X] > player_pos[X]:
            self.speed[X] += -1*self.acc[X]
            if(self.speed[X]<=-self.max_speed[X]):
                self.speed[X]=-self.max_speed[X]
        if self.pos[Y] < player_pos[Y]:
            self.speed[Y] += self.acc[Y]
            if(self.speed[Y]>=self.max_speed[Y]):
                self.speed[Y]=self.max_speed[Y]
        elif self.pos[Y] >player_pos[Y]:
            self.speed[Y] += -1*self.acc[Y]
            if(self.speed[Y]<=-self.max_speed[Y]):
                self.speed[Y]=-self.max_speed[Y]
        if (self.speed[X] > 0 and self.pos[X] >= player_pos[X]) or (self.speed[X] < 0 and self.pos[X] <= player_pos[X]):
            self.speed[X] = 0
            self.pos[X] = player_pos[X]
        
        if (self.speed[Y] > 0 and self.pos[Y] >= player_pos[Y]) or (self.speed[Y] < 0 and self.pos[Y] <= player_pos[Y]):
            self.speed[Y] = 0
            self.pos[Y] = player_pos[Y]

        if self.frame >= self.STATE_DURATION[State.MOVE]:
            self.change_state(State.WAIT)
    
    def update_wait(self, player_pos):
        if self.frame >= self.STATE_DURATION[State.WAIT]:
            self.change_state(State.MOVE)
        
    def collide_map_x(self, rect):
        pass
    
    def collide_map_y(self, rect):
        pass
    
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