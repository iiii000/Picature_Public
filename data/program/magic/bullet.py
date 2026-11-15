import math
import pygame

from core.config import *

class Bullet:
    def __init__(self, start, end):
        self.alive = True
        self.damage = 5

        self.pos = list(end)
        self.speed = 10

        # 線から方向ベクトルを取得
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        # 正規化（長さを1にする）
        length = math.hypot(dx, dy)
        if length == 0:
            length = 1

        self.vx = dx / length * self.speed
        self.vy = dy / length * self.speed

        self.radius = 10
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.radius*2, self.radius*2)

    def update(self):
        self.pos[0] += self.vx
        self.pos[1] += self.vy
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))
        if (self.pos[0] < -50 or self.pos[0] > WINDOW_SIZE[0] + 50 or
            self.pos[1] < -50 or self.pos[1] > WINDOW_SIZE[1] + 50):
            self.delete()

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.radius)
        #pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)
    
    def delete(self):
        self.alive = False
    
    def collide_map(self):
        self.alive = False