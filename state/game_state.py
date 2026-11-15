import pygame

class Game_state:
    def __init__(self, stage):
        self.stage = stage
        self.exit_requested = False

    def enter(self, game):
        if self.stage.event_requested:
            game.set_next_state('Event')

    def handle_events(self, game):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.exit_requested = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.exit_requested = True

        self.stage.handle_events(events)
    
    def update(self, game):
        self.stage.update()
        if self.stage.goal_requested:
            game.next_stage()
        if self.exit_requested:
            game.set_next_state('Exit')

    def draw(self, game):
        self.stage.draw(game.virtual_surface)