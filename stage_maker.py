import pygame
from pygame.locals import *
import sys
import csv
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple

from core.config import *

pygame.init()

WORLD_NUM = 1

CANVAS_SIZE = (1920, 1080)
TILE_NUM = (30, 16)
UI_NUM = 0
START_GOAL_NUM = 1
BACKGROUND_NUM = 1
ENEMY_NUM = 1
GIMMICK_NUM = 1

info = pygame.display.Info()
VIRTUAL_WINDOW_SIZE = (CANVAS_SIZE[X] + TILE_SIZE * UI_NUM, CANVAS_SIZE[Y] + TILE_SIZE * (START_GOAL_NUM+BACKGROUND_NUM+ENEMY_NUM+GIMMICK_NUM))
REAL_WINDOW_SIZE = (info.current_w, info.current_h)

FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 20)
BIGFONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 28)

@dataclass
class MapData:
    event: int = 0
    specific_gimmick: int = 0
    start_pos: Tuple[int,int] = (0*TILE_SIZE,1*TILE_SIZE)
    goal_pos: Tuple[int,int] = (1*TILE_SIZE,1*TILE_SIZE)
    backgrounds: List[int] = field(default_factory=list)
    enemy_types: List[int] = field(default_factory=list)
    enemy_positions: List[Tuple[int,int]] = field(default_factory=list)

@dataclass
class GimmickData:
    gimmick_types: List[int] = field(default_factory=list)
    gimmick_positions: List[Tuple[int,int]] = field(default_factory=list)

class Main:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            REAL_WINDOW_SIZE,
            pygame.FULLSCREEN
        )

        self.virtual_surface = pygame.Surface(VIRTUAL_WINDOW_SIZE)
        self.scaled_surface = pygame.Surface(REAL_WINDOW_SIZE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.map_maker = MapMaker()

        self.game_state = 'Stage_Maker'

    def run(self):
        """メインループ"""
        while self.running:
            if self.game_state == 'Stage_Maker':
                self.handle_events()
                self.update()
                self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        self.quit()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        self.map_maker.handle_events(events)

    def update(self):
        self.map_maker.update()

    def draw(self):
        self.virtual_surface.fill((0, 0, 0))
        self.map_maker.draw(self.virtual_surface)

        # --- スケーリング ---
        pygame.transform.scale(
            self.virtual_surface,
            REAL_WINDOW_SIZE,
            self.scaled_surface
        )

        self.screen.blit(self.scaled_surface, (0, 0))

    def quit(self):
        pygame.quit()
        sys.exit()

class MapMaker:
    def __init__(self):
        self.state = "edit" # "edit" or "export" or "load"

        self.palette = PALETTE()
        self.canvas = CANVAS(self.palette.start_goal,self.palette.backgrounds, self.palette.enemy_images, self.palette.gimmicks)
        #self.ui = UI()
        self.INPUT_BOX = InputBox(100, 100, 200, 40, FONT)

    def handle_events(self, events):
        if self.state == "export" or self.state == "load":
            self.INPUT_BOX.handle_event(events)
        else:
            self.palette.handle_events(events)
            self.canvas.handle_events(events, self.palette.tool_type, self.palette.tool)
            #self.ui.handle_events(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.state == "edit":
                    if event.key == pygame.K_s:  # 's'キーでエクスポート開始
                        self.state = "export"
                        self.INPUT_BOX.state = "save_directory"  # ディレクトリ入力モードに切り替え
                        self.INPUT_BOX.set_data(self.canvas.map_data, self.canvas.gimmick_data)  # マップデータをInputBoxに渡す  
                    elif event.key == pygame.K_l:  # 'l'キーでロード開始
                        self.state = "load"
                        self.INPUT_BOX.state = "load_directory"  # ディレクトリ入力モードに切り替え

    def update(self):
        if self.state == "export" or self.state == "load":
            self.INPUT_BOX.update()
        else:
            self.palette.update()
            self.canvas.update()
            #self.ui.update()
        if self.state == "load":
            if self.INPUT_BOX.state == "inactive":
                self.canvas.platforms = self.INPUT_BOX.platforms
                self.canvas.platform_height = self.INPUT_BOX.platfotm_height
                self.canvas.map_data = self.INPUT_BOX.map_data
                self.canvas.gimmick_data = self.INPUT_BOX.gimmick_data
                self.INPUT_BOX.set_data(None, None)  # データをクリア
                self.canvas.create_surface()  # マップを再描画
                self.state = "edit"  # 入力が完了したら編集モードに戻る

    def draw(self, screen):
        self.canvas.draw(screen)
        self.palette.draw(screen)
        #self.ui.draw(screen)
        if self.state == "export" or self.state == "load":
            self.INPUT_BOX.draw(screen)

class CANVAS():
    def __init__(self, start_goal, backgrounds, enemy_images, gimmicks):
        self.platform_height = 0
        self.platforms = []
        self.map_data = MapData()
        self.gimmick_data = GimmickData()

        self.start_goal = start_goal
        self.backgrounds = backgrounds
        self.enemy_images = enemy_images
        self.gimmicks = gimmicks

        self.map_surface = pygame.Surface(CANVAS_SIZE, pygame.SRCALPHA)
        self.map_surface.fill((0, 0, 0, 0))  # 透明にする
        self.map_surface.convert_alpha()
        self.create_surface()
    
    def handle_events(self, events, tool_type, tool):
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            virtual_x = int(mouse_x * VIRTUAL_WINDOW_SIZE[0] / REAL_WINDOW_SIZE[0])
            virtual_y = int(mouse_y * VIRTUAL_WINDOW_SIZE[1] / REAL_WINDOW_SIZE[1])
            grid_x = virtual_x // TILE_SIZE
            grid_y = round((virtual_y - self.platform_height) / TILE_SIZE)
            if tool_type == 0 and tool == 2:
                self.map_data.event = 1
            elif tool_type == 0 and tool == 3:
                self.map_data.specific_gimmick = 1
            if 0 <= virtual_x < CANVAS_SIZE[X] and 0 <= virtual_y < CANVAS_SIZE[Y]:
                if tool_type == 0 and tool == 0:
                    self.map_data.start_pos = (grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)  # スタート位置を配置
                elif tool_type == 0 and tool == 1:
                    self.map_data.goal_pos = (grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)  # ゴール位置を配置
                if tool_type == 0 and tool == 4:
                    self.platform_height = virtual_y
                elif tool_type == 1 and self.map_data.backgrounds.count(tool) == 0:  # 同じ背景IDがない場合のみ追加
                    self.map_data.backgrounds.append(tool)  # 背景IDを配置
                elif tool_type == 2 and (self.map_data.enemy_positions.count((grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)) == 0):  # 同じ位置に敵がいない場合のみ追加
                    self.map_data.enemy_positions.append((grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height))
                    self.map_data.enemy_types.append(tool)  # 敵IDを配置
                elif tool_type == 3 and (self.gimmick_data.gimmick_positions.count((grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)) == 0):  # 同じ位置にギミックがいない場合のみ追加
                    self.gimmick_data.gimmick_positions.append((grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height))
                    self.gimmick_data.gimmick_types.append(tool)  # ギミックIDを配置
            self.create_surface()  # 変更があったらマップを再描画
            

        elif pygame.mouse.get_pressed()[2]:  # 右クリックで削除
            mouse_x, mouse_y = pygame.mouse.get_pos()
            virtual_x = int(mouse_x * VIRTUAL_WINDOW_SIZE[0] / REAL_WINDOW_SIZE[0])
            virtual_y = int(mouse_y * VIRTUAL_WINDOW_SIZE[1] / REAL_WINDOW_SIZE[1])
            grid_x = virtual_x // TILE_SIZE
            grid_y = round((virtual_y - self.platform_height) / TILE_SIZE)
            if tool_type == 0 and tool == 2:
                    self.map_data.event = 0
            elif tool_type == 0 and tool == 3:
                    self.map_data.specific_gimmick = 0
            elif tool_type == 1:
                self.map_data.backgrounds = [bg for bg in self.map_data.backgrounds if bg != grid_x]  # 背景IDを削除
            if 0 <= virtual_x < CANVAS_SIZE[X] and 0 <= virtual_y < CANVAS_SIZE[Y]:
                if tool_type == 2:
                    self.map_data.enemy_positions = [(ex, ey) for ex, ey in self.map_data.enemy_positions if (ex, ey) != (grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)]
                    self.map_data.enemy_types = [etype for etype, (ex, ey) in zip(self.map_data.enemy_types, self.map_data.enemy_positions) if (ex, ey) != (grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)]
                elif tool_type == 3:
                    self.gimmick_data.gimmick_positions = [(gx, gy) for gx, gy in self.gimmick_data.gimmick_positions if (gx, gy) != (grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)]
                    self.gimmick_data.gimmick_types = [gtype for gtype, (gx, gy) in zip(self.gimmick_data.gimmick_types, self.gimmick_data.gimmick_positions) if (gx, gy) != (grid_x*TILE_SIZE, grid_y*TILE_SIZE+self.platform_height)]
            self.create_surface()  # 変更があったらマップを再描画

        elif pygame.mouse.get_pressed()[1]:  # 中クリックでプラットフォームの高さをリセット
            self.map_data = MapData()  # マップデータを初期化
            self.gimmick_data = GimmickData()  # ギミックデータを初期化
            self.create_surface()  # 変更があったらマップを再描画
    
    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.map_surface, (0, 0))
        pygame.draw.line(screen, (255, 0, 0), (0, self.platform_height), (VIRTUAL_WINDOW_SIZE[X], self.platform_height), 2)  # プラットフォームの高さを示す赤い線
    
    def create_surface(self):
        self.map_surface.fill((0, 0, 0, 0))  # 透明にする
        self.create_background_surface()
        self.create_platform_surface()
        self.create_start_goal_surface()
        self.create_enemy_surface()
        self.create_gimmick_surface()

    def create_background_surface(self):
        for bg_id in self.map_data.backgrounds:
            if 0 <= bg_id < len(self.backgrounds):
                bg = self.backgrounds[bg_id]
                self.map_surface.blit(bg, (0, 0))

    def create_platform_surface(self):
        for platform in self.platforms:
            self.map_surface.blit(platform, (0, 0))

    def create_start_goal_surface(self):
        self.map_surface.blit(self.start_goal[0], (self.map_data.start_pos[X], self.map_data.start_pos[Y]))
        self.map_surface.blit(self.start_goal[1], (self.map_data.goal_pos[X], self.map_data.goal_pos[Y]))
        if self.map_data.event == 1:
            self.map_surface.blit(self.start_goal[2], (0, 0))
        if self.map_data.specific_gimmick == 1:
            self.map_surface.blit(self.start_goal[3], (1 * TILE_SIZE, 0))

    def create_enemy_surface(self):
        for enemy_id, (ex, ey) in zip(self.map_data.enemy_types, self.map_data.enemy_positions):
            if 0 <= enemy_id < len(self.enemy_images):
                enemy_img = self.enemy_images[enemy_id]
                self.map_surface.blit(enemy_img, (ex, ey))

    def create_gimmick_surface(self):
        for gimmick_id, (gx, gy) in zip(self.gimmick_data.gimmick_types, self.gimmick_data.gimmick_positions):
            if 0 <= gimmick_id < len(self.gimmicks):
                gimmick_img = self.gimmicks[gimmick_id]
                self.map_surface.blit(gimmick_img, (gx, gy))

class PALETTE():
    def __init__(self):
        self.world_num = WORLD_NUM
        self.start_goal = []
        self.backgrounds = []
        self.enemy_images = []
        self.gimmicks = []

        self.tool_type = 0  # 0:start_goal, 1:backgrounds, 2:enemies, 3:gimmicks
        self.tool = 0  # 現在のツール（タイルID）
        self.palette_surface = pygame.Surface((TILE_SIZE * TILE_NUM[X], TILE_SIZE*(START_GOAL_NUM+BACKGROUND_NUM+ENEMY_NUM+GIMMICK_NUM)))
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        self.load_start_goal()
        self.load_backgrounds()
        self.load_enemies()
        self.load_gimmicks()
        self.create_palette()

    def handle_events(self, events):
        if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:  # 左クリックまたは右クリック
            mouse_x, mouse_y = pygame.mouse.get_pos()
            virtual_x = int(mouse_x * VIRTUAL_WINDOW_SIZE[0] / REAL_WINDOW_SIZE[0])
            virtual_y = int(mouse_y * VIRTUAL_WINDOW_SIZE[1] / REAL_WINDOW_SIZE[1])
            tool_type = (virtual_y - CANVAS_SIZE[Y]) // TILE_SIZE  # ツールタイプを計算
            index = virtual_x // TILE_SIZE  # ツールのインデックスを計算
            if tool_type == 0:
                self.tool_type = 0 # スタート/ゴール選択
                if 0 <= index < len(self.start_goal):
                    self.tool = index
                    self.rect.topleft = (index * TILE_SIZE, CANVAS_SIZE[Y])  # ツールの選択枠を移動
            elif tool_type == 1:
                self.tool_type = 1 # 背景選択
                if 0 <= index < len(self.backgrounds):
                    self.tool = index
                    self.rect.topleft = (index * TILE_SIZE, CANVAS_SIZE[Y] + TILE_SIZE)
            elif tool_type == 2:
                self.tool_type = 2  # 敵選択
                if 0 <= index < len(self.enemy_images):
                    self.tool = index
                    self.rect.topleft = (index * TILE_SIZE, CANVAS_SIZE[Y] + TILE_SIZE * 2)
            elif tool_type == 3:
                self.tool_type = 3  # ギミック選択
                if 0 <= index < len(self.gimmicks):
                    self.tool = index
                    self.rect.topleft = (index * TILE_SIZE, CANVAS_SIZE[Y] + TILE_SIZE * 3)

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.palette_surface, (0, CANVAS_SIZE[Y]))
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 3)  # 選択枠を描画

    def create_palette(self):
        self.palette_surface.fill((50, 50, 50))  # パレットの背景色
        for i, sg in enumerate(self.start_goal):
            self.palette_surface.blit(sg, (i * TILE_SIZE, 0))
        for i, bg in enumerate(self.backgrounds):
            bg = pygame.transform.scale(bg, (TILE_SIZE, TILE_SIZE))
            self.palette_surface.blit(bg, (i * TILE_SIZE, TILE_SIZE))
        for i, enemy in enumerate(self.enemy_images):
            enemy = pygame.transform.scale(enemy, (TILE_SIZE, TILE_SIZE))
            self.palette_surface.blit(enemy, (i * TILE_SIZE, TILE_SIZE * 2))
        for i, gimmick in enumerate(self.gimmicks):
            gimmick = pygame.transform.scale(gimmick, (TILE_SIZE, TILE_SIZE))
            self.palette_surface.blit(gimmick, (i * TILE_SIZE, TILE_SIZE * 3))

    def load_backgrounds(self):
        self.backgrounds = []
        bg_dir = f'assets/background/{self.world_num}'
        if os.path.isdir(bg_dir):
            # フォルダ内のすべてのPNGファイルを読み込む
            bg_files = sorted([f for f in os.listdir(bg_dir) if f.endswith('.png')])
            for bg_file in bg_files:
                bg_path = os.path.join(bg_dir, bg_file)
                img = pygame.transform.smoothscale(pygame.image.load(bg_path).convert_alpha(), (TILE_SIZE * TILE_NUM[X], TILE_SIZE * TILE_NUM[Y]))
                self.backgrounds.append(img)

    def load_enemies(self):
        self.enemy_images = []
        enemy_dir = "assets/enemy"

        if os.path.isdir(enemy_dir):
            enemy_folders = sorted(
                d for d in os.listdir(enemy_dir)
                if os.path.isdir(os.path.join(enemy_dir, d))
            )

            for folder in enemy_folders:

                idle_dir = os.path.join(enemy_dir, folder, "idle")

                if not os.path.isdir(idle_dir):
                    continue

                image_files = sorted(
                    f for f in os.listdir(idle_dir)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                )

                if not image_files:
                    continue

                first_image_path = os.path.join(idle_dir, image_files[0])

                img = pygame.image.load(first_image_path).convert_alpha()
                self.enemy_images.append(
                    pygame.transform.scale(img, ENEMY_SIZE)
                )

    def load_start_goal(self):
        self.start_goal = [self.create_start_goal_marker_surface(i) for i in range(5)]
    
    def create_start_goal_marker_surface(self, number):
        marker = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        marker = marker.convert_alpha()
        center = (TILE_SIZE // 2, TILE_SIZE // 2)
        radius = TILE_SIZE // 2 - 8

        if number == 0:
            color = (0, 255, 255)
        elif number == 1:
            color = (0, 255, 255)
        elif number == 2:
            color = (0, 0, 255) 
        elif number == 3:
            color = (0, 0, 255)
        elif number == 4:
            color = (255, 255, 0)
        pygame.draw.circle(marker, color, center, radius)
        pygame.draw.circle(marker, (0, 0, 0), center, radius, 3)

        if number == 0:
            text = FONT.render("S", True, (0, 0, 0))
        elif number == 1:
            text = FONT.render("G", True, (0, 0, 0))
        elif number == 2:
            text = FONT.render("E", True, (0, 0, 0))
        elif number == 3:
            text = FONT.render("SG", True, (0, 0, 0))
        elif number == 4:
            text = FONT.render("PH", True, (0, 0, 0))
        text_rect = text.get_rect(center=center)
        marker.blit(text, text_rect)

        return marker

    def load_gimmicks(self):
        self.gimmicks = [self.create_gimmick_marker_surface(i) for i in range(10)]

    def create_gimmick_marker_surface(self, number):
        marker = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        marker = marker.convert_alpha()
        center = (TILE_SIZE // 2, TILE_SIZE // 2)
        radius = TILE_SIZE // 2 - 8

        pygame.draw.circle(marker, (255, 255, 255), center, radius)
        pygame.draw.circle(marker, (0, 0, 0), center, radius, 3)

        text = FONT.render(str(number), True, (0, 0, 0))
        text_rect = text.get_rect(center=center)
        marker.blit(text, text_rect)

        return marker

class UI:
    def __init__(self):
        pass

    def load_palette(self):
        pass  # UIは背景の概念に依存しないため、特に更新は不要

    def handle_events(self, events):
        pass  # UIのイベント処理は、必要に応じて実装

    def draw(self, screen):
        pass  # UIの描画は、必要に応じて実装

class InputBox:
    def __init__(self, x, y, w, h, font, text=""):
        self.surface = pygame.Surface((w, h))
        self.surface.fill((0, 0, 0, 0))  # 透明にする
        self.surface.convert_alpha()
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.directory = text
        self.file_name = text
        self.state = "inactive"  # "inactive", "save_directory", "save_file_name", "load_directory", "load_file_name", "exporting", "loading"

        self.color_inactive = (150, 150, 150)
        self.color_active = (255, 255, 255)
        self.color = self.color_inactive

        self.platforms = []
        self.platfotm_height = 0
        self.map_data = None
        self.gimmick_data = None

    def handle_event(self, events):
        # キー入力
        if self.state != "inactive" and self.state != "exporting" and self.state != "loading":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # 's'キーでエクスポート開始
                        if self.state == "save_directory":
                            self.state = "save_file_name"
                        elif self.state == "save_file_name":
                            self.state = "exporting"
                            self.export()  # エクスポート処理を呼び出す
                            self.state = "inactive"
                        elif self.state == "load_directory":
                            self.state = "load_file_name"
                        elif self.state == "load_file_name":
                            self.state = "loading"
                            self.load()  # ロード処理を呼び出す（実装する場合）
                            self.state = "inactive"

                    elif event.key == pygame.K_BACKSPACE:
                        if self.state == "save_directory" and len(self.directory) > 0:
                            self.directory = self.directory[:-1]
                        elif self.state == "save_file_name" and len(self.file_name) > 0:
                            self.file_name = self.file_name[:-1]
                        elif self.state == "load_directory" and len(self.directory) > 0:
                            self.directory = self.directory[:-1]
                        elif self.state == "load_file_name" and len(self.file_name) > 0:
                            self.file_name = self.file_name[:-1]

                    else:
                        if self.state == "save_directory":
                            self.directory += event.unicode
                        elif self.state == "save_file_name":
                            self.file_name += event.unicode
                        elif self.state == "load_directory":
                            self.directory += event.unicode
                        elif self.state == "load_file_name":
                            self.file_name += event.unicode

    def update(self):
        if self.state == "save_directory":
            # テキスト幅に応じてボックス拡張（任意）
            width = max(200, self.font.size(self.directory)[0] + 20)
            self.rect.w = width
        elif self.state == "save_file_name":
            width = max(200, self.font.size(self.file_name)[0] + 20)
            self.rect.w = width
        elif self.state == "load_directory":
            width = max(200, self.font.size(self.directory)[0] + 20)
            self.rect.w = width
        elif self.state == "load_file_name":
            width = max(200, self.font.size(self.file_name)[0] + 20)
            self.rect.w = width

    def draw(self, screen):
        if self.state == "save_directory":
            # テキスト描画
            txt_surface = self.font.render(self.directory, True, (255, 255, 255))
            screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))
        elif self.state == "save_file_name":
            txt_surface = self.font.render(self.file_name, True, (255, 255, 255))
            screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))
        elif self.state == "load_directory":
            txt_surface = self.font.render(self.directory, True, (255, 255, 255))
            screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))
        elif self.state == "load_file_name":
            txt_surface = self.font.render(self.file_name, True, (255, 255, 255))
            screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))

        # 枠描画
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def set_data(self, map_data, gimmick_data):
        self.platforms = []
        self.platfotm_height = 0
        self.map_data = map_data
        self.gimmick_data = gimmick_data

    def export(self):
        self.export_map_data()
        self.export_gimmick_data()

    def export_map_data(self):
        # 保存先ディレクトリ
        save_dir = Path("data/csv/map_data") / self.directory

        # ディレクトリが無ければ作る
        save_dir.mkdir(parents=True, exist_ok=True)

        # ファイルパス作成
        file_path = save_dir / f"{self.file_name}.csv"

        # 書き込み
        with file_path.open("w", newline="") as f:
            writer = csv.writer(f)

            # 固定部分
            writer.writerow([self.map_data.event])
            writer.writerow([self.map_data.specific_gimmick])
            self.map_data.start_pos = (self.map_data.start_pos[X], self.map_data.start_pos[Y]+TILE_SIZE-CHARA_SIZE[Y])
            writer.writerow(self.map_data.start_pos)
            writer.writerow(self.map_data.goal_pos)
            writer.writerow(self.map_data.backgrounds)  # 背景IDのリストを保存

            # 敵（タイプ + 座標をペアで書く）
            for etype, (x, y) in zip(self.map_data.enemy_types, self.map_data.enemy_positions):
                writer.writerow([etype])
                writer.writerow([x, y])
    
    def export_gimmick_data(self):
        # 保存先ディレクトリ
        save_dir = Path("data/csv/gimmick_data") / self.directory

        # ディレクトリが無ければ作る
        save_dir.mkdir(parents=True, exist_ok=True)

        # ファイルパス作成
        file_path = save_dir / f"{self.file_name}.csv"

        # 書き込み
        with file_path.open("w", newline="") as f:
            writer = csv.writer(f)

            # ギミックをタイプごとにグループ化
            from collections import defaultdict
            gimmick_groups = defaultdict(list)
            for gtype, (x, y) in zip(self.gimmick_data.gimmick_types, self.gimmick_data.gimmick_positions):
                gimmick_groups[gtype].append((x, y))

            # 各タイプごとにタイプを一行、座標を同じ行にまとめて一行
            for gtype, positions in gimmick_groups.items():
                writer.writerow([gtype])
                row = []
                for x, y in positions:
                    row.extend([x, y])
                writer.writerow(row)

    def load(self):
        self.load_platforms()
        self.load_map_data()
        self.load_gimmick_data()

    def load_platforms(self):
        loaded_num = []
        platform_dir = f'assets/platform/{self.directory}/{self.file_name}'
        if os.path.isdir(platform_dir):
            platform_files = sorted([f for f in os.listdir(platform_dir) if f.endswith('.png')])
            for platform_file in platform_files:
                platform_num = int(platform_file.split('-')[0])
                if platform_num not in loaded_num:
                    platform_path = os.path.join(platform_dir, platform_file)
                    img = pygame.transform.scale(pygame.image.load(platform_path).convert_alpha(), CANVAS_SIZE)
                    self.platforms.append(img)
                    loaded_num.append(platform_num)
        rect = self.platforms[0].get_bounding_rect()
        self.platfotm_height = rect.top

    def load_map_data(self):
        # 読み込み先ディレクトリ
        load_dir = Path("data/csv/map_data") / self.directory
        file_path = load_dir / f"{self.file_name}.csv"

        self.map_data = MapData()

        if not file_path.exists():
            return

        # 読み込み
        with file_path.open("r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

            self.map_data.event = int(rows[0][0]) if len(rows) > 0 else 0
            self.map_data.specific_gimmick = int(rows[1][0]) if len(rows) > 1 else 0
            self.map_data.start_pos = tuple(int(x) for x in rows[2]) if len(rows) > 2 else (0, 1)
            self.map_data.goal_pos = tuple(int(x) for x in rows[3]) if len(rows) > 3 else (1, 1)
            self.map_data.backgrounds = [int(x) for x in rows[4]] if len(rows) > 4 and rows[4] else []

            # 敵
            self.map_data.enemy_types = []
            self.map_data.enemy_positions = []
            for i in range(5, len(rows), 2):
                if i + 1 < len(rows):
                    self.map_data.enemy_types.append(int(rows[i][0]))
                    self.map_data.enemy_positions.append(tuple(int(x) for x in rows[i+1]))

    def load_gimmick_data(self):
        # 読み込み先ディレクトリ
        load_dir = Path("data/csv/gimmick_data") / self.directory
        file_path = load_dir / f"{self.file_name}.csv"
        
        self.gimmick_data = GimmickData()

        if not file_path.exists():
            return

        # 読み込み
        with file_path.open("r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

            self.gimmick_data.gimmick_types = []
            self.gimmick_data.gimmick_positions = []

            i = 0
            while i < len(rows):
                gtype = int(rows[i][0])
                i += 1
                if i < len(rows):
                    coords = [int(x) for x in rows[i]]
                    for j in range(0, len(coords), 2):
                        self.gimmick_data.gimmick_types.append(gtype)
                        self.gimmick_data.gimmick_positions.append((coords[j], coords[j+1]))
                    i += 1

if __name__ == "__main__":
    main = Main()
    main.run()