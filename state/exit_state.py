class Exit_state:
    def __init__(self):
        pass

    def enter(self, game):
        game.running = False
    
    def handle_events(self, game):
        pass
    
    def update(self, game):
        pass

    def draw(self, game):
        pass