import pygame

from core.event_manager import Event_manager

class Event_state():
    def __init__(self, stage):
        self.stage = stage
        self.event_manager = Event_manager(self.stage)
        self.exit_requested = False

    def enter(self, game):
        pass

    def handle_events(self, game):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.exit_requested = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.exit_requested = True
    
    def update(self, game):
        self.event_manager.update()
        if self.exit_requested:
            game.set_next_state('Exit')
        if self.event_manager.event_end_requested:
            game.set_next_state('Game')
    
    def draw(self, game):
        self.event_manager.draw(game.virtual_surface)
