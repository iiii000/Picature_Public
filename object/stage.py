import csv
from dataclasses import dataclass, field
from typing import Tuple, List

from core.config import *
from core.collision import Collision
from object.map import map
from object.gimmicks import Gimmicks
from object.goal import Goal
from object.enemies import Enemies
from object.player import Player
from object.lines import Line

@dataclass
class MapData:
    event: int = 0
    specific_gimmick: int = 0
    start_position: Tuple[int,int] = (0,0)
    goal_position: Tuple[int,int] = (1,0)
    backgrounds: List[int] = field(default_factory=list)
    enemy_types: List[int] = field(default_factory=list)
    enemy_positions: List[List[Tuple[int,int]]] = field(default_factory=list)

@dataclass
class GimmickData:
    gimmick_types: List[int] = field(default_factory=list)
    gimmick_ids: List[int] = field(default_factory=list)
    gimmick_positions: List[Tuple[int,int]] = field(default_factory=list)
    
class Stage():
    def __init__(self, world_num, stage_num):
        self.world_num = world_num
        self.stage_num = stage_num

        self.event_requested = False
        self.goal_requested = False

        self.map_data = self.load_map_data()
        self.gimmick_data = self.load_gimmick_data()
        
        self.map = map(self.map_data, self.world_num, self.stage_num)
        self.gimmicks = Gimmicks(self.gimmick_data, self.map_data.specific_gimmick)
        self.goal = Goal(self.map_data)
        self.enemies = Enemies(self.map_data)
        self.player = Player(self.map_data)
        self.line = Line()
        self.collision = Collision()

    def handle_events(self, events):
        self.player.handle_events(events)
        self.line.handle_events(events)

    def update(self):
        self.map.update()
        self.gimmicks.update()
        self.goal.update()
        self.enemies.update(self.player.rect)
        self.player.update()
        self.line.update(self.player)
        self.collision_check()
        self.collision_resolve()
        if self.player.restart_requested:
            self.restart()
    
    def restart(self):
        self.player.restart()
        self.enemies.restart(self.map_data)
        self.gimmicks.restart(self.gimmick_data, self.map_data.specific_gimmick)
        self.line.restart()
    def draw(self, screen):
        self.map.draw(screen)
        self.gimmicks.draw(screen)
        self.goal.draw(screen)
        self.enemies.draw(screen)
        self.player.draw(screen)
        self.line.draw(screen)
    def collision_check(self):
        self.player.move_x()
        self.enemies.move_x()
        self.collision.check_x(self.player, self.enemies, self.map, self.line, self.gimmicks, self.goal)
        self.player.move_y()
        self.enemies.move_y()
        self.collision.check_y(self.player, self.enemies, self.map, self.line, self.gimmicks, self.goal)
        self.collision.check(self.player, self.enemies, self.map, self.line, self.gimmicks, self.goal)
        if self.collision.player_goal(self.player, self.goal):
            self.goal_requested = True

    def collision_resolve(self):
        self.player.collision_resolve()
        self.enemies.collision_resolve()

    def load_map_data(self):
        map_data = MapData()
        filename = f'data/csv/map_data/{self.world_num}/{self.stage_num}.csv'
        with open(filename, encoding='utf8', newline='') as file:
            tmp = list(csv.reader(file))
        map_data.event = int(tmp[0][0])
        if int(tmp[1][0]) == 0:
            map_data.specific_gimmick = None
        else:
            map_data.specific_gimmick = f"{self.world_num}-{self.stage_num}"
        map_data.start_position = [int(tmp[2][0]), int(tmp[2][1])]
        map_data.goal_position = [int(tmp[3][0]), int(tmp[3][1])]
        # 背景番号はtmp[4]の全要素
        map_data.backgrounds = [int(i) for i in tmp[4]] if len(tmp) > 4 else []

        # 敵データは行5以降、2行ずつ（敵種と位置）
        for i in range(5, len(tmp), 2):
            if i + 1 < len(tmp):
                enemy_type = int(tmp[i][0])
                positions_raw = tmp[i + 1]
                positions = [(int(positions_raw[j]), int(positions_raw[j + 1]))for j in range(0, len(positions_raw), 2)]

                map_data.enemy_types.append(enemy_type)
                map_data.enemy_positions.append(positions)
        
        if map_data.event != 0:
            self.event_requested = True
        
        return map_data

    def load_gimmick_data(self):
        gimmick_data = GimmickData()
        filename = f'data/csv/gimmick_data/{self.world_num}/{self.stage_num}.csv'
        with open(filename, encoding='utf8', newline='') as file:
            tmp = list(csv.reader(file))
        
        for i in range(0, len(tmp), 2):
            gimmick_data.gimmick_types.append(int(tmp[i][0]))
            gimmick_data.gimmick_ids.append(int(tmp[i][1]))
            gimmick_data.gimmick_positions.append((int(tmp[i+1][0]), int(tmp[i+1][1])))
        
        return gimmick_data