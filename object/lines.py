import pygame

from core.config import *
from data.program.magic.bullet import Bullet

class Line():
    def __init__(self):
        self.surface = pygame.Surface((VIRTUAL_WINDOW_SIZE), pygame.SRCALPHA)
        self.lines = []  # 各要素は[[(x1,y1), (x2,y2), ...], ...]
        self.current_line = []
        self.mask = None
        self.count = 0
        self.spell=[]
        self.magics = []

        self.is_hold = False
        self.is_draw = False

    def handle_events(self, events):
        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                mx, my = event.pos

                # 仮想座標へ変換（超重要）
                vmx = int(mx / SCALE_X)
                vmy = int(my / SCALE_Y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_hold = True
                self.is_draw = True
                self.current_line = [(vmx, vmy)]

            elif event.type == pygame.MOUSEMOTION and self.is_draw:
                self.current_line.append((vmx, vmy))

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_hold:
                self.is_hold = False
                self.is_draw = False

    def update(self, player):
        if self.current_line != [] and self.is_hold == False:
            if len(self.current_line) > 1:
                if any(player.rect.collidepoint(point) for point in self.current_line):
                    player.dush(self.current_line.copy())
                else:
                    self.lines.append(self.current_line.copy())
                    self.create_mask()
                    self.check_line()
                    self.count += 1
            self.current_line = []

        if self.get_line_length(self.current_line) > MAX_LINE_LENGTH:
            self.is_draw = False
            
        if self.count == 3:
            self.check_magic()
            
        if self.magics != []:
            for i in self.magics:
                i.update()
            self.delete_magic()

    def draw(self, screen):
        # 毎フレームクリア（超重要）
        self.surface.fill((0, 0, 0, 0))

        time = pygame.time.get_ticks() * 0.002

        # 保存済みの線
        for line in self.lines:
            for i in range(len(line) - 1):
                p1 = line[i]
                p2 = line[i + 1]

                hue = (time + i * 0.02) % 1.0
                color = self.hsv_to_rgb(hue, 1, 1)

                pygame.draw.line(self.surface, (*color, 80), p1, p2, 8)  # 外側ぼんやり
                pygame.draw.line(self.surface, color, p1, p2, 4)
                pygame.draw.line(self.surface, color, p1, p2, 2)          # 中心

        # 描画中の線
        if self.is_hold and len(self.current_line) > 1:
            for i in range(len(self.current_line) - 1):
                p1 = self.current_line[i]
                p2 = self.current_line[i + 1]

                hue = (time + i * 0.02) % 1.0
                color = self.hsv_to_rgb(hue, 1, 1)

                pygame.draw.line(self.surface, (*color, 80), p1, p2, 8)  # 外側ぼんやり
                pygame.draw.line(self.surface, color, p1, p2, 4)          # 中心

                pygame.draw.line(self.surface, color, p1, p2, 2)

        screen.blit(self.surface, (0, 0))
        if self.magics != []:
            for i in self.magics:
                i.draw(screen)
    
    def create_mask(self):
        temp_surface = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)

        for line in self.lines:
            pygame.draw.lines(temp_surface, (255,255,255), False, line, 8)

        self.mask = pygame.mask.from_surface(temp_surface)

    def hsv_to_rgb(self, h, s, v):
        i = int(h * 6)
        f = h * 6 - i
        p = int(255 * v * (1 - s))
        q = int(255 * v * (1 - f * s))
        t = int(255 * v * (1 - (1 - f) * s))
        v = int(255 * v)
        i = i % 6

        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)
    
    def check_magic(self):
        if self.spell == [0,1,1]:
            self.magics.append(Bullet(self.lines[0][0], self.lines[0][len(self.lines[0])-1]))

        self.surface = pygame.Surface((VIRTUAL_WINDOW_SIZE[0], VIRTUAL_WINDOW_SIZE[1]), pygame.SRCALPHA)
        self.lines = []  # 各要素は[[(x1,y1), (x2,y2), ...], ...]
        self.mask = None
        self.count = 0
        self.spell=[]
    
    def delete_magic(self):
        # 画面外、またはaliveがFalseの魔法を削除
        self.magics = [i for i in self.magics if i.alive]

    def check_line(self):
        line = self.lines[self.count]
        length = self.get_line_length(line)
        if length>300:
            self.spell.append(0)
        elif length<=300:
            self.spell.append(1)

    def get_line_length(self, line):
        length = 0
        for i in range(len(line) - 1):
            x1, y1 = line[i]
            x2, y2 = line[i+1]
            length += ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
        return length
    
    def restart(self):
        self.surface = pygame.Surface((VIRTUAL_WINDOW_SIZE), pygame.SRCALPHA)
        self.lines = []  # 各要素は[[(x1,y1), (x2,y2), ...], ...]
        self.current_line = []
        self.mask = None
        self.is_draw = False
        self.count = 0
        self.spell=[]
        self.magics = []