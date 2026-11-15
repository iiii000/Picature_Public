import csv

import pygame
from pygame.locals import *

from core.config import *

class Event_manager():
    def __init__(self, stage):
        self.stage = stage

        self.frame = 0
        self.event_frame = []
        self.event_object = []
        self.event_type = []

        self.stage.player.is_event = True
        self.event_end_requested = False

        self.load_event()
    
    def update(self):
        if self.frame == self.event_frame[0]:
            if self.event_object[0] == "end":
                self.stage.player.is_event = False
                self.stage.event_requested = False
                self.event_end_requested = True
                
            elif self.event_object[0] == "player":
                if self.event_type[0] == "shake":
                    self.stage.player.is_shake = True
                elif self.event_type[0] == "stop":
                    self.stage.player.is_shake = False
                else:
                    self.stage.player.state = self.event_type[0]
            self.event_frame.pop(0)
            self.event_object.pop(0)
            self.event_type.pop(0)
        self.frame += 1

        self.stage.update()
    
    def draw(self, screen):
        self.stage.draw(screen)

    def load_event(self):
        filename = f'data/event/{self.stage.map_num}-{self.stage.stage_num}.csv'
        with open(filename, encoding='utf8', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                self.event_frame.append(int(row[0]))
                self.event_object.append(row[1])
                self.event_type.append(row[2])