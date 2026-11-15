import pygame

from core.config import *

class Title:
    def __init__(self):
        self.screen_width, self.screen_height = VIRTUAL_WINDOW_SIZE

        # フォント
        self.title_font = pygame.font.Font(None, 80)
        self.menu_font = pygame.font.Font(None, 50)

        # メニュー
        self.menu_items = ["Start", "Option", "Exit"]
        self.selected_index = 0

        # フラグ（State側が見る）
        self.start_requested = False
        self.option_requested = False
        self.exit_requested = False

    def handle_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                elif event.key == pygame.K_s:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                elif event.key == pygame.K_SPACE:
                    self._select()

    def _select(self):
        selected = self.menu_items[self.selected_index]

        if selected == "Start":
            self.start_requested = True

        elif selected == "Option":
            self.option_requested = True

        elif selected == "Exit":
            self.exit_requested = True

    def update(self):
        pass  # 今は特に処理なし（アニメーション追加できる）

    def draw(self, screen):
        screen.fill((0, 0, 0))

        # --- タイトル ---
        title_text = self.title_font.render("MY GAME", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(title_text, title_rect)

        # --- メニュー ---
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 255)

            # 選択中は色変更
            if i == self.selected_index:
                color = (255, 255, 0)

            text = self.menu_font.render(item, True, color)

            # 縦に並べる
            x = self.screen_width // 2
            y = self.screen_height // 2 + i * 60

            rect = text.get_rect(center=(x, y))
            screen.blit(text, rect)