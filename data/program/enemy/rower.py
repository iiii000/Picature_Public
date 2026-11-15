from enum import Enum, auto
from pathlib import Path
import pygame
from pygame.locals import *

from core.config import *
from .enemy_base import Enemy

class State(Enum):
    IDLE = auto()
    SEARCH = auto()
    ATTACK = auto()
    WAIT = auto()

class Rower(Enemy):
    enemy_id = 3
    
    STATE_DURATION = {
        State.IDLE: 60,
        State.SEARCH: 60,
        State.ATTACK: 10,
        State.WAIT: 20,
    }

    STATE_IMAGE = {
        State.IDLE: 0,       # idle画像
        State.SEARCH: 0,   # しゃがみ
        State.ATTACK: 0,       # 跳躍
        State.WAIT: 0,    # 着地余韻
    }

    def __init__(self, init_pos):
        self.alive = True
        self.max_hp = 10
        self.hp = self.max_hp
        self.attack_power = 10
        self.search_range = 100
        self.attack_range = 5

        self.imagelist = {
            State.IDLE: [],
            State.SEARCH: [],
            State.ATTACK: [],
            State.WAIT: [],
        }

        self.reverse_imagelist = {
            State.IDLE: [],
            State.SEARCH: [],
            State.ATTACK: [],
            State.WAIT: [],
        }

        self.rect = None
        self.bullets = []

        self.init_pos = list(init_pos[0])
        self.pos = self.init_pos.copy()

        self.acc = [1,1]
        self.max_speed = [0, 4]
        self.jump_power = 0
        self.speed = [0, 0]

        self.is_attack = False
        self.is_right = False
        self.is_ground = False

        # 状態管理
        self.state = State.IDLE
        self.frame = 0

        self.load_image()

        # 状態更新関数
        self.state_update = {
            State.IDLE: self.update_idle,
            State.SEARCH: self.update_search,
            State.ATTACK: self.update_attack,
            State.WAIT: self.update_wait,
        }

    def update(self, player_pos):
        self.frame += 1
        if self.frame == 10 * ENEMY_ANIMATION_SPEED * len(self.imagelist[self.state]):
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
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

        if self.bullets != []:
            for i in self.bullets:
                i.draw(screen)

    def update_idle(self, player_pos):
        if (self.pos[Y]-self.search_range<=player_pos[Y] and self.pos[Y]+self.search_range>=player_pos[Y]):
            self.change_state(State.SEARCH)

    def update_search(self, player_pos):
        if (self.pos[Y]-self.attack_range<=player_pos[Y] and self.pos[Y]+self.attack_range>=player_pos[Y]):
            self.change_state(State.ATTACK)
        elif (self.pos[Y]<player_pos[Y]):
            self.speed[Y]+=self.acc[Y]
            if(self.speed[Y]>=self.max_speed[Y]):
                self.speed[Y]=self.max_speed[Y]
        elif (self.pos[Y]>player_pos[Y]):
            self.speed[Y]+=-1*self.acc[Y]
            if(self.speed[Y]<=-self.max_speed[Y]):
                self.speed[Y]=-self.max_speed[Y]
        
    def update_attack(self, player_pos):
        if self.speed[Y] > 0:
            self.speed[Y] += -1*self.acc[Y]
        elif self.speed[Y] < 0:
            self.speed[Y] += self.acc[Y]
        
        if self.is_attack == 0 and self.speed[X] == 0:
            self.frame = 0
            self.is_attack = 1
            self.bullets.append(Bullet(self.rect.midleft, player_pos))
        
        if self.is_attack == 1 and self.frame == self.STATE_DURATION[State.ATTACK]:
            self.is_attack = 0
            self.change_state(State.WAIT)

    def update_wait(self, player_pos):
        if(self.frame==self.STATE_DURATION[State.WAIT]):
            if self.pos[X]-self.search_range<=player_pos[X] and player_pos[X] <= self.pos[X]+self.search_range:
                self.change_state(State.SEARCH)
            else:
                self.change_state(State.IDLE)
    
    def collide_player(self, player):
        if player.is_dush and not player.is_attacked:
            player.is_attacked = True
            self.damage(player.attack_power)
        elif not player.is_dush:
            player.damage(self.attack_power)
    
    def restart(self):
        self.alive = True
        self.hp = self.max_hp
        self.pos = self.init_pos.copy()
        self.speed = [0, 0]
        self.frame = 0
        self.state = State.IDLE
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
    def __init__(self, enemy_pos, player_pos):
        self.alive = True
        self.damage = 10

        self.pos = list(enemy_pos).copy()
        self.speed = 50

        self.radius = 10
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.radius*2, self.radius*2)
        self.pos_checker(player_pos)

    def update(self):
        self.pos[X] += self.speed
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))
        if (self.pos[0] < -50 or self.pos[0] > WINDOW_SIZE[0] + 50 or
            self.pos[1] < -50 or self.pos[1] > WINDOW_SIZE[1] + 50):
            self.delete()

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.radius)
        #pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)
    
    def pos_checker(self, player_pos):
        if player_pos[X] < self.pos[X]:
            self.speed = -1*self.speed
    
    def collide_player(self, player):
        self.delete()
        player.damage(self.damage)
    
    def collide_map(self):
        self.delete()
    
    def delete(self):
        self.alive = False