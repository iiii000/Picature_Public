from enum import Enum, auto
from pathlib import Path
import random
import pygame
from pygame.locals import *

from core.config import *
from .enemy_base import Enemy

ENEMY_SIZE = [475, 254]
RECT_SIZE = [200, 254]

class State(Enum):
    IDLE = auto()
    WALK = auto()
    JUMP_START = auto()
    JUMP = auto()
    JUMP_END = auto()
    STAB = auto()
    CHARGE_START = auto()
    CHARGE = auto()
    CHARGE_END = auto()
    WEB_START = auto()
    WEB = auto()
    WEB_END = auto()

class Spider(Enemy):
    enemy_id = 5
    STATE_DURATION = {
        State.IDLE: [-1, 30],
        State.WALK: [10, 30],
        State.JUMP_START: [0, 0],
        State.JUMP: [0, 0],
        State.JUMP_END: [0, 0],
        State.STAB: [0, 0],
        State.CHARGE_START: [0, 0],
        State.CHARGE: [0, 0],
        State.CHARGE_END: [0, 0],
        State.WEB_START: [0, 0],
        State.WEB: [0, 0],
        State.WEB_END: [0, 0],
    }
    IMAGE_NUM = {
        State.WEB_START: [],
        State.JUMP_START: [4],
        State.JUMP_END: [4],
        State.CHARGE_START: [12],
        State.CHARGE_END: [6],
        State.WEB_START: [4],
        State.WEB_END: [4],
    }

    def __init__(self, init_pos):
        self.alive = True
        self.max_hp = 20
        self.hp = self.max_hp
        self.attack_power = 10
        self.move_range = 100
        self.attack_range = [40, 200]

        self.imagelist = {
            State.IDLE: [],
            State.WALK: [],
            State.JUMP_START: [],
            State.JUMP: [],
            State.JUMP_END: [],
            State.STAB: [],
            State.CHARGE_START: [],
            State.CHARGE: [],
            State.CHARGE_END: [],
            State.WEB_START: [],
            State.WEB: [],
            State.WEB_END: [],
        }

        self.reverse_imagelist = {
            State.IDLE: [],
            State.WALK: [],
            State.JUMP_START: [],
            State.JUMP: [],
            State.JUMP_END: [],
            State.STAB: [],
            State.CHARGE_START: [],
            State.CHARGE: [],
            State.CHARGE_END: [],
            State.WEB_START: [],
            State.WEB: [],
            State.WEB_END: [],
        }

        self.image_rect = None
        self.attack_rect = None
        self.rect = pygame.Rect(0, 0, RECT_SIZE[X], RECT_SIZE[Y])
        self.bullets = []

        self.init_pos = list(init_pos[0])
        self.pos = self.init_pos.copy()
        self.move_pos = list(init_pos[1:])

        self.acc = [1,2]
        self.max_speed = [10, 20]
        self.jump_power = 40
        self.charge_speed = 100
        self.speed = [0, 0]

        self.is_attack = False
        self.is_ground = False
        self.is_move = False
        self.is_right = False
        self.is_edge = False
        self.is_wall = False

        # 状態管理
        self.state = State.IDLE
        self.frame = 0
        self.image_num = -1

        self.max_jump_count = 3
        self.jump_rates = [0.8, 0.5, 0.25, 0.1]
        self.jump_count = 0

        self.load_image()

        # 状態更新関数
        self.state_update = {
            State.IDLE: self.update_idle,
            State.WALK: self.update_walk,
            State.JUMP_START: self.update_jump_start,
            State.JUMP: self.update_jump,
            State.JUMP_END: self.update_jump_end,
            State.STAB: self.update_stab,
            State.CHARGE_START: self.update_charge_start,
            State.CHARGE: self.update_charge,
            State.CHARGE_END: self.update_charge_end,
            State.WEB_START: self.update_web_start,
            State.WEB: self.update_web,
            State.WEB_END: self.update_web_end
        }

    def update(self, player_rect):
        self.frame += 1
        if self.frame == 10 * ENEMY_ANIMATION_SPEED * len(self.imagelist[self.state]):
            self.frame = 0

        self.speed[Y] += self.acc[Y]
        if self.speed[Y] > self.max_speed[Y]:
            self.speed[Y] = self.max_speed[Y]

        self.state_update[self.state](player_rect)
        
        self.image_num = int(self.frame/ENEMY_ANIMATION_SPEED) % len(self.imagelist[self.state])

        if self.hp <= 0:
            self.delete()

        if self.bullets != []:
            for i in self.bullets:
                i.update(self.state, self.rect, self.image_num)
            self.bullets = [i for i in self.bullets if i.alive]

    def draw(self, screen):
        if self.is_right:
            image = self.reverse_imagelist[self.state][self.image_num]
        else:
            image = self.imagelist[self.state][self.image_num]
        screen.blit(image, self.image_rect)
        #pygame.draw.rect(screen, (255, 0, 0), self.image_rect, 2)
        #pygame.draw.rect(screen, (0, 0, 255), self.attack_rect, 2)
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

        if self.bullets != []:
            for i in self.bullets:
                i.draw(screen)

    def update_idle(self, player_rect):
        self.speed[X] = 0

        if self.frame >= self.STATE_DURATION[self.state][1]:
            self.face_player(player_rect)

            if self.hp < self.max_hp / 2:
                self.random_state((State.WEB_START, 30), (self.State.WALK, 20), (State.JUMP_START, 30), (State.CHARGE_START, 30))
            else:
                self.random_state((State.WALK, 60), (State.JUMP_START, 0), (State.CHARGE_START, 0))


    def update_walk(self, player_rect):
        direction = 1 if self.is_right else -1
        self.speed[X] = self.max_speed[X] * direction

        if self.frame >= self.STATE_DURATION[self.state][0]:
            if self.attack_rect.colliderect(player_rect):
                self.choose_attack(player_rect)

        if self.frame >= self.STATE_DURATION[self.state][1]:
            self.speed[X] = 0
            self.change_state(State.CHARGE_START)


    def update_jump_start(self, player_rect):
        self.speed[X] = 0

        if self.image_num == self.IMAGE_NUM[State.JUMP_START][0]:
            self.face_player(player_rect)
            direction = 1 if self.is_right else -1
            self.speed[X] = self.max_speed[X] * direction
            self.speed[Y] = -1 * self.jump_power
            self.is_ground = False
            self.change_state(State.JUMP)



    def update_jump(self, player_rect):
        if self.is_ground:
            self.speed[X] = 0
            self.speed[Y] = 0
            self.change_state(State.JUMP_END)


    def update_jump_end(self, player_rect):
        if self.image_num != self.IMAGE_NUM[State.JUMP_END][0]:
            return

        if self.jump_count < self.max_jump_count:
            rate = self.jump_rates[self.jump_count]

            if random.random() < rate:
                self.jump_count += 1
                self.change_state(State.JUMP_START)
                return

        self.jump_count = 0
        self.change_state(State.IDLE)


    def update_stab(self, player_rect):
        self.speed[X] = 0

        if self.image_num == self.IMAGE_NUM[State.STAB][0]:
            self.bullets.append(Stab(self.is_right, self.IMAGE_NUM[State.STAB], self.rect, player_rect))

        if self.image_num >= self.IMAGE_NUM[State.STAB][2]:
            self.random_state(State.WALK, State.JUMP_START)


    def update_charge_start(self, player_rect):
        if self.image_num == self.IMAGE_NUM[State.CHARGE_START][0]:
            self.is_wall = False
            direction = 1 if self.is_right else -1
            self.speed[X] = self.charge_speed * direction
            self.bullets.append(Charge(self.is_right, self.rect))
            self.change_state(State.CHARGE)


    def update_charge(self, player_rect):
        if self.is_wall:
            self.change_state(State.CHARGE_END)


    def update_charge_end(self, player_rect):
        if self.image_num == self.IMAGE_NUM[State.CHARGE_END][0]:
            self.random_state((State.IDLE, 60), (State.WALK, 30), (State.JUMP_START, 10))


    def update_web_start(self, player_rect):
        if self.image_num == self.IMAGE_NUM[State.WEB_START][0]:
            self.start_jump_to_player(player_rect)


    def update_web(self, player_rect):
        self.bullets.append(Bullet(self.rect, player_rect))
        self.change_state(State.WAIT)


    def update_web_end(self, player_rect):
        pass

    def collide_map_x(self, rect):
        if self.speed[X] > 0:
            self.rect.right = rect.left
        elif self.speed[X] < 0:
            self.rect.left = rect.right
        self.speed[X] = 0
        self.is_move = 0
        self.is_wall = True
    
    def collision_resolve(self):
        self.image_rect.midbottom = self.rect.midbottom
        self.attack_rect.midbottom = self.rect.midbottom
        self.pos[X] = self.image_rect.x
        self.pos[Y] = self.image_rect.y
    
    def collide_player(self, player):
        if player.is_dush and not player.is_attacked:
            player.is_attacked = True
            self.damage(player.attack_power)
        elif not player.is_dush:
            player.damage(self.attack_power)
        
    def change_state(self, new_state):
        self.state = new_state
        self.image_num = 0
        self.frame = 0

    def face_player(self, player_rect):
        if self.rect.centerx < player_rect.centerx:
            self.is_right = 1
        elif self.rect.centerx > player_rect.centerx:
            self.is_right = 0

    def random_state(self, *state_weights):
        states, weights = zip(*state_weights)
        self.change_state(random.choices(states, weights=weights, k=1)[0])
    
    def choose_attack(self, player_rect):
        if self.hp < self.max_hp / 2 and random.randint(0, 1) == 0:
            self.change_state(State.WEB)
            return
        
        if random.randint(0, 1) == 0:
            self.change_state(State.CHARGE)
            return

        if self.rect.top < player_rect.bottom:
            self.change_state(State.STAB)
        elif self.rect.top > player_rect.bottom:
            self.change_state(State.JUMP_START)
    
    def restart(self):
        self.alive = True
        self.hp = self.max_hp
        self.pos = self.init_pos.copy()
        self.speed = [0, 0]

        self.image_rect.topleft = self.pos
        self.attack_rect.midbottom = self.image_rect.midbottom
        self.rect.midbottom = self.image_rect.midbottom

        self.bullets = []

        self.is_attack = False
        self.is_ground = False
        self.is_move = False
        self.is_right = False

        # 状態管理
        self.state = State.IDLE
        self.frame = 0
        self.image_num = -1
    
    def load_image(self):
        enemy_name = self.__class__.__name__.lower()
        base_path = Path("assets/enemy") / enemy_name
        for state in State:
            state_name = state.name.lower()
            state_path = base_path / state_name
            images = []
            for img_path in sorted(state_path.glob("*.png")):
                img = pygame.image.load(str(img_path)).convert_alpha()
                img = pygame.transform.scale(img, (ENEMY_SIZE[X], ENEMY_SIZE[Y]))
                images.append(img)
            self.imagelist[state] = images
            self.reverse_imagelist[state] = [pygame.transform.flip(img, True, False) for img in images]
        self.image_rect = self.imagelist[state.IDLE][0].get_rect()
        self.attack_rect = self.image_rect.copy()
        self.attack_rect.height += self.attack_range[Y]
        self.image_rect.x = self.init_pos[0]
        self.image_rect.y = self.init_pos[1]
        self.rect.midbottom = self.image_rect.midbottom
        self.attack_rect.midbottom = self.image_rect.midbottom

class Charge():
    def __init__(self, is_right, enemy_rect):
        self.alive = True
        self.damage = 10
        self.is_right = is_right

        self.rect = pygame.Rect(0, 0, 150, ENEMY_SIZE[Y]-100)
        self.set_rect(enemy_rect)

    def update(self, state, enemy_rect, image_num):
        if self.is_right:
            self.rect.midleft = enemy_rect.midright
        else:
            self.rect.midright = enemy_rect.midleft
        if state == State.CHARGE_END:
            self.delete()

    def draw(self, screen):
        pass
        #pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)
    
    def collide_player(self, player):
        self.delete()
        player.damage(self.damage)
    
    def collide_map(self):
        pass
    
    def delete(self):
        self.alive = False
    
    def set_rect(self, enemy_rect):
        if self.is_right:
            self.rect.midleft = enemy_rect.midright
        else:
            self.rect.midright = enemy_rect.midleft

class Stab():
    def __init__(self, is_right, attack_duration, enemy_rect, player_rect):
        self.alive = True
        self.damage = 10

        self.attack_duration = attack_duration

        self.rect = pygame.Rect(0, 0, 150, ENEMY_SIZE[Y])
        self.set_rect(is_right, enemy_rect)

    def update(self, state, image_num):
        if image_num == self.attack_duration[1]:
            self.delete()

    def draw(self, screen):
        pass
        #pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)
    
    def collide_player(self, player):
        self.delete()
        player.damage(self.damage)
    
    def collide_map(self):
        pass
    
    def delete(self):
        self.alive = False
    
    def set_rect(self, is_right, enemy_rect):
        if is_right:
            self.rect.bottomleft = enemy_rect.bottomright
        else:
            self.rect.bottomright = enemy_rect.bottomleft

class Bullet():
    def __init__(self, enemy_pos, player_rect):
        self.alive = True
        self.damage = 10
        self.frame = 0
        self.end_frame = 180

        self.pos = list(enemy_pos).copy()

        self.radius = 100
        self.rect = pygame.Rect(0,0, self.radius*2, self.radius*2)
        self.rect.center = self.pos

    def update(self, state, image_num):
        self.frame += 1
        if self.frame >= self.end_frame:
            self.delete()

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.radius)
        #pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)
    
    def collide_player(self, player):
        self.delete()
        player.damage(self.damage)
    
    def collide_map(self):
        pass
    
    def delete(self):
        self.alive = False