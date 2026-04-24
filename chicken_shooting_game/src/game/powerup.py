import pygame
import random
from ..utils.config import SCREEN_HEIGHT, BLUE, RED, YELLOW, CYAN, WHITE, GREEN

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype=None):
        super().__init__()
        # Expanded powerups
        pool = ["upgrade", "spread", "laser", "rocket", "shield", "health", "coin", "bomb", "magnet", "speed"]
        self.type = ptype if ptype else random.choice(pool)
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        
        self.colors = {
            "upgrade": (255, 100, 255), # Magenta
            "spread": (50, 255, 50),    # Green
            "laser": (255, 50, 50),     # Red
            "shield": (200, 255, 255),  # Cyan
            "rocket": (255, 150, 0),    # Orange
            "bomb": (100, 100, 100),    # Grey
            "health": (255, 50, 150),   # Pink
            "coin": (255, 215, 0),      # Gold
            "magnet": (150, 50, 255),   # Purple
            "speed": (50, 150, 255)     # Blue
        }
        self.draw_powerup()

    def draw_powerup(self):
        color = self.colors.get(self.type, WHITE)
        # Hexagonal shape for powerup
        pygame.draw.polygon(self.image, color, [
            (15, 0), (30, 8), (30, 22), (15, 30), (0, 22), (0, 8)
        ])
        pygame.draw.polygon(self.image, WHITE, [
            (15, 0), (30, 8), (30, 22), (15, 30), (0, 22), (0, 8)
        ], 2)
        
        font = pygame.font.SysFont("Arial", 16, bold=True)
        letter_map = {
            "upgrade": "^", "spread": "S", "laser": "L", "shield": "O", 
            "rocket": "R", "bomb": "B", "health": "+", "coin": "$",
            "magnet": "U", "speed": ">>"
        }
        text = font.render(letter_map.get(self.type, "?"), True, WHITE)
        self.image.blit(text, (15 - text.get_width()//2, 15 - text.get_height()//2))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
