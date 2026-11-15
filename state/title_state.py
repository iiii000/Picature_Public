import pygame

from ui.title import Title

class Title_state:
    def __init__(self):
        self.title = Title()
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

        self.title.handle_event(events)

    def update(self, game):
        self.title.update()
        if self.title.start_requested:
            game.set_next_state('Game')
        if self.title.exit_requested:
            game.set_next_state('Exit')
        if self.exit_requested:
            game.set_next_state('Exit')

    def draw(self, game):
        self.title.draw(game.virtual_surface)