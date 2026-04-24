import pygame
import random
import math
from ..utils.config import SCREEN_WIDTH, RED, WHITE, BLUE, YELLOW, ORANGE, BLACK, EGG_SPAWN_CHANCE, SCREEN_HEIGHT
from .egg import Egg
from .food import Food
from .powerup import PowerUp

class Chicken(pygame.sprite.Sprite):
    def __init__(self, level=1, chicken_type="regular", target_x=SCREEN_WIDTH//2, target_y=100):
        super().__init__()
        import os
        img_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', 'chicken_base.png')
        if os.path.exists(img_path):
            self.base_image = pygame.image.load(img_path).convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (60, 60))
        else:
            self.base_image = pygame.Surface((60, 60), pygame.SRCALPHA)
            
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        
        self.target_x = target_x
        self.target_y = target_y
        self.hover_center_x = target_x
        
        self.rect.x = target_x
        self.rect.y = -60 - random.randint(0, 300) # Staggered entry
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        
        self.level = level
        self.type = chicken_type
        self.state = "ENTERING" # ENTERING, HOVERING, SWOOPING
        self.time = random.uniform(0, 10) # random phase offset
        
        # Base stats
        self.hp = 1
        self.speed = 1.5 + level * 0.4
        self.color = WHITE
        
        if self.type == "turbo":
            self.speed *= 1.8
            self.color = YELLOW
        elif self.type == "zigzag":
            self.speed *= 1.2
            self.color = RED
            self.hp = 2

        self.draw_chicken()

    def draw_chicken(self):
        # Start fresh with the base image sprite
        if hasattr(self, 'base_image'):
            self.image = self.base_image.copy()
        else:
            self.image.fill((0, 0, 0, 0))
            
        # Draw type indicators
        if self.type == "turbo":
            # Add a yellow aura/engine glow effect
            pygame.draw.circle(self.image, (255, 255, 100, 100), (30, 30), 30, 3)
            pygame.draw.circle(self.image, ORANGE, (15, 55), 6)
            pygame.draw.circle(self.image, ORANGE, (45, 55), 6)
        elif self.type == "zigzag":
            # Add a red angry aura
            pygame.draw.circle(self.image, (255, 50, 50, 150), (30, 30), 30, 4)

    def update(self, dt=1.0, player_x=SCREEN_WIDTH//2):
        self.time += 0.05 * dt
        
        if self.state == "ENTERING":
            # Move down to target_y
            if self.y < self.target_y:
                self.y += self.speed * 2 * dt
            else:
                self.y = self.target_y
                self.state = "HOVERING"
                
            self.rect.y = int(self.y)
            self.rect.x = int(self.x)
            
        elif self.state == "HOVERING":
            # Sway left and right
            sway_amount = 150 if self.type != "zigzag" else 300
            self.x = self.hover_center_x + math.sin(self.time) * sway_amount
            self.rect.x = int(self.x)
            
            # small chance to swoop (Medium Difficulty)
            if random.random() < 0.0005 * dt:
                self.state = "SWOOPING"
                self.swoop_target_x = player_x
                self.swoop_vx = (self.swoop_target_x - self.x) * 0.02
                
        elif self.state == "SWOOPING":
            # Dive bomb
            self.y += self.speed * 3 * dt
            self.x += self.swoop_vx * dt
            self.rect.y = int(self.y)
            self.rect.x = int(self.x)
            
            # Reset if goes off screen
            if self.y > SCREEN_HEIGHT + 100:
                self.y = -100
                self.x = self.target_x
                self.state = "ENTERING"

    def reset(self):
        # In CIU, chickens don't usually 'respawn' when killed, they die.
        # But if we need to reset one (e.g. player hit it), we just kill it instead,
        # or send it back to entering state.
        self.y = -100
        self.x = self.target_x
        self.state = "ENTERING"

    def try_drop_egg(self, speed_multiplier=1.0):
        if random.random() < EGG_SPAWN_CHANCE:
            return Egg(self.rect.centerx, self.rect.bottom)
        return None

    def try_drop_loot(self):
        # Tăng tỷ lệ rơi vật phẩm kỹ năng (từ bản nâng cấp mới)
        rand = random.random()
        if rand < 0.20: # 20% cơ hội rớt kỹ năng (tăng gấp 4)
             return PowerUp(self.rect.centerx, self.rect.centery)
        elif rand < 0.55: # 35% cơ hội rớt thức ăn
             return Food(self.rect.centerx, self.rect.centery)
        return None

class Formation:
    @staticmethod
    def _create_chicken(level, ctype, target_x, target_y):
        return Chicken(level, ctype, target_x, target_y)

    @staticmethod
    def create_grid(level, cols=5, rows=3):
        chickens = []
        start_x = SCREEN_WIDTH // 2 - ((cols - 1) * 80) // 2
        start_y = 80
        for r in range(rows):
            for c in range(cols):
                ctype = "turbo" if random.random() < 0.15 else ("zigzag" if random.random() < 0.1 else "regular")
                chickens.append(Formation._create_chicken(level, ctype, start_x + c * 80, start_y + r * 60))
        return chickens

    @staticmethod
    def create_v_shape(level, size=5):
        chickens = []
        center_x = SCREEN_WIDTH // 2
        start_y = 80
        for i in range(size):
            ctype = "turbo" if random.random() < 0.2 else "regular"
            chickens.append(Formation._create_chicken(level, ctype, center_x - i * 80, start_y + i * 60))
            if i > 0:
                chickens.append(Formation._create_chicken(level, ctype, center_x + i * 80, start_y + i * 60))
        return chickens
        
    @staticmethod
    def create_circle(level, radius=150, count=10):
        chickens = []
        center_x = SCREEN_WIDTH // 2
        center_y = 200
        for i in range(count):
            angle = math.pi * 2 * (i / count)
            ctype = "zigzag" if random.random() < 0.2 else "regular"
            tx = center_x + math.cos(angle) * radius
            ty = center_y + math.sin(angle) * radius
            chickens.append(Formation._create_chicken(level, ctype, tx, ty))
        return chickens
        
    @staticmethod
    def create_x_shape(level, size=5):
        chickens = []
        center_x = SCREEN_WIDTH // 2
        center_y = 200
        for i in range(-size//2, size//2 + 1):
            ctype = "turbo" if random.random() < 0.15 else "regular"
            chickens.append(Formation._create_chicken(level, ctype, center_x + i * 80, center_y + i * 80))
            if i != 0:
                chickens.append(Formation._create_chicken(level, ctype, center_x + i * 80, center_y - i * 80))
        return chickens

    @staticmethod
    def create_diamond(level, size=3):
        chickens = []
        center_x = SCREEN_WIDTH // 2
        center_y = 200
        for i in range(-size, size + 1):
            space = size - abs(i)
            chickens.append(Formation._create_chicken(level, "regular", center_x - space * 80, center_y + i * 60))
            if space > 0:
                chickens.append(Formation._create_chicken(level, "turbo", center_x + space * 80, center_y + i * 60))
        return chickens

    @staticmethod
    def create_u_shape(level, width=6, height=3):
        chickens = []
        start_x = SCREEN_WIDTH // 2 - ((width - 1) * 80) // 2
        start_y = 80
        for c in range(width):
            chickens.append(Formation._create_chicken(level, "regular", start_x + c * 80, start_y + height * 60))
        for r in range(height):
            chickens.append(Formation._create_chicken(level, "zigzag", start_x, start_y + r * 60))
            chickens.append(Formation._create_chicken(level, "zigzag", start_x + (width - 1) * 80, start_y + r * 60))
        return chickens

    @staticmethod
    def get_wave(level, wave):
        functions = [
            lambda l: Formation.create_grid(l, max(4, min(8, 4 + l//2)), max(3, min(5, 3 + l//4))),
            lambda l: Formation.create_v_shape(l, max(4, min(7, 3 + l//2))),
            lambda l: Formation.create_circle(l, 100 + l*10, max(8, min(20, 8 + l))),
            lambda l: Formation.create_x_shape(l, max(3, min(7, 3 + l//3))),
            lambda l: Formation.create_diamond(l, max(3, min(5, 2 + l//3))),
            lambda l: Formation.create_u_shape(l, max(5, min(8, 4 + l//2)), max(3, min(5, 3 + l//4)))
        ]
        
        # We handle the 5 waves per level inside game.py, here we just return a valid wave
        func = random.choice(functions)
        return func(level)
