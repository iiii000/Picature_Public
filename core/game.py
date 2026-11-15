import sys

import pygame

from core.config import *
from state.title_state import Title_state
from state.game_state import Game_state
from state.event_state import Event_state
from state.exit_state import Exit_state
from object.stage import Stage

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)

        info = pygame.display.Info()
        SET_WINDOW_SIZE([info.current_w, info.current_h])
        self.screen = pygame.display.set_mode(
            WINDOW_SIZE,
            pygame.FULLSCREEN
        )
        self.virtual_surface = pygame.Surface(VIRTUAL_WINDOW_SIZE)
        self.scaled_surface = pygame.Surface(WINDOW_SIZE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.world_num = 1
        self.stage_num = 3

        self.current_state = Title_state()
        self.next_state = None
        self.stage = Stage(self.world_num, self.stage_num)

    def run(self):
        while self.running:
            self.current_state.handle_events(self)
            self.current_state.update(self)
            self.current_state.draw(self)
            self.draw()
            while self.next_state is not None:
                self.change_state()
            # FPS取得
            fps = self.clock.get_fps()
            fps_text = self.font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
            # 描画
            self.screen.blit(fps_text, (10, 10))
            pygame.display.flip()
            self.clock.tick(FPS)
        self.quit()
    
    def draw(self):
        pygame.transform.scale(
            self.virtual_surface,
            WINDOW_SIZE,
            self.scaled_surface
        )

        self.screen.blit(self.scaled_surface, (0, 0))

    def change_state(self):
        if self.next_state is None:
            return
        elif self.next_state == 'Title':
            self.current_state = Title_state()
        elif self.next_state == 'Game':
            self.current_state = Game_state(self.stage)
        elif self.next_state == 'Event':
            self.current_state = Event_state(self.stage)
        elif self.next_state == 'Exit':
            self.current_state = Exit_state()
        self.next_state = None
        self.current_state.enter(self)
    
    def set_next_state(self, state):
        self.next_state = state

    def next_stage(self):
        self.stage_num += 1
        self.stage = Stage(self.world_num, self.stage_num)
        self.set_next_state('Game')

    def quit(self):
        pygame.quit()
        sys.exit()