import pygame

# =========================
# 画面設定
# =========================
# ディスプレイ解像度を取得
WINDOW_SIZE = [1920, 1080]
VIRTUAL_WINDOW_SIZE = [1920, 1080]
SCALE_X = WINDOW_SIZE[0] / VIRTUAL_WINDOW_SIZE[0]
SCALE_Y = WINDOW_SIZE[1] / VIRTUAL_WINDOW_SIZE[1]
FPS = 60

# =========================
# 色
# =========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# =========================
# プレイヤー設定
# =========================
PLAYER_HP = 10
PLAYER_ACC = [1,2]
PLAYER_MAX_SPEED = [10, 20]
PLAYER_JUMP_POWER = 20
MAX_STEP_HEIGHT = 1 
MAX_LINE_LENGTH = 500

# =========================
# 敵設定
# =========================
SEARCH_RANGE = 100
ATTACK_RANGE = 5

# =========================
# タイル
# =========================
TILE_SIZE = 64
TILE_NUM = [30, 16]
CHARA_SIZE = [120, 120]
ENEMY_SIZE = [128, 128]
RECT_OFFSET = 10

# =========================
# カスタムイベント
# =========================
GAME_START = pygame.USEREVENT + 1
EXIT = pygame.USEREVENT + 2
GOAL_REACHED = pygame.USEREVENT + 3
EVENT_START = pygame.USEREVENT + 4
EVENT_END = pygame.USEREVENT + 5

# =========================
# その他
# =========================
PLAYER_ANIMATION_SPEED = 5
ENEMY_ANIMATION_SPEED = 5
MAP_ANIMATION_SPEED = 8
DEBUG = True
X=0
Y=1

def SET_WINDOW_SIZE(size):
    global WINDOW_SIZE
    WINDOW_SIZE = size
    global SCALE_X, SCALE_Y
    SCALE_X = WINDOW_SIZE[0] / VIRTUAL_WINDOW_SIZE[0]
    SCALE_Y = WINDOW_SIZE[1] / VIRTUAL_WINDOW_SIZE[1]