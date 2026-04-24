import pygame

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors (Advanced Palette)
WHITE = (255, 255, 255)
BLACK = (5, 5, 15)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 150, 50)
PURPLE = (150, 50, 250)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)

# Game balance
PLAYER_SPEED = 10
BULLET_SPEED = 15
CHICKEN_SPEED_BASE = 2
CHICKEN_SCORE = 10
LEVEL_UP_SCORE = 500
CHICKENS_PER_LEVEL = 15 # Required kills to advance level

# Skill Cooldowns (frames @ 60FPS)
ULTIMATE_COOLDOWN = 300 # 5s
BOMB_COOLDOWN = 600     # 10s
SLOW_MO_COOLDOWN = 900  # 15s

# Mechanics
MAX_HP = 5 # Medium difficulty (was 3)
EGG_SPEED = 4
EGG_SPAWN_CHANCE = 0.003

# Boss settings
BOSS_LEVEL_1 = 5
BOSS_LEVEL_2 = 10
BOSS_HP_BASE = 50
Boss_SPEED = 1
