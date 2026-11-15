import importlib

from data.program.gimmick.switch import Switch
from data.program.gimmick.door import Door

class Gimmicks():
    def __init__(self, gimmick_data, is_sg):
        self.gimmicks = []
        self.specific_gimmick = None
        self.load_gimmicks(gimmick_data, is_sg)

    def update(self):
        for gimmick in self.gimmicks:
            gimmick.update()
        if self.specific_gimmick:
            self.specific_gimmick.update()

    def draw(self, screen):
        for gimmick in self.gimmicks:
            gimmick.draw(screen)
        if self.specific_gimmick:
            self.specific_gimmick.draw(screen)

    def load_gimmicks(self, data, is_sg):
        if is_sg:
                module = importlib.import_module(f"data.program.specific_gimmick.{is_sg}")
                class_name = "specific_gimmick"
                gimmick_class = getattr(module, class_name)
                self.specific_gimmick = gimmick_class()
        for type, id, position in zip(data.gimmick_types, data.gimmick_ids, data.gimmick_positions):
            if type == 0:
                self.gimmicks.append(Switch(id, position[0]))
            elif type == 1:
                self.gimmicks.append(Door(id, position))
    
    def restart(self, gimmick_data, is_sg):
        self.gimmicks = []
        self.specific_gimmick = None
        self.load_gimmicks(gimmick_data, is_sg)