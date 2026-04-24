import pygame
import random
from ..utils.config import SCREEN_HEIGHT, YELLOW, ORANGE, WHITE, RED

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y, ftype=None):
        super().__init__()
        # Randomize food types
        self.type = ftype if ftype else random.choice(["drumstick", "burger", "pizza"])
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(3, 5)
        
        if self.type == "drumstick": self.score = 50
        elif self.type == "burger": self.score = 100
        elif self.type == "pizza": self.score = 150
            
        self.draw_food()

    def draw_food(self):
        if self.type == "drumstick":
            # Bone
            pygame.draw.rect(self.image, WHITE, (13, 15, 4, 12))
            pygame.draw.circle(self.image, WHITE, (12, 25), 4)
            pygame.draw.circle(self.image, WHITE, (18, 25), 4)
            # Meat
            pygame.draw.ellipse(self.image, (150, 75, 0), (6, 2, 18, 18))
            pygame.draw.ellipse(self.image, (200, 100, 20), (8, 4, 14, 12)) # Shine
        elif self.type == "burger":
            # Buns
            pygame.draw.ellipse(self.image, (210, 150, 80), (2, 4, 26, 12))
            pygame.draw.ellipse(self.image, (210, 150, 80), (2, 20, 26, 8))
            # Meat & Lettuce
            pygame.draw.rect(self.image, (100, 50, 20), (3, 14, 24, 6))
            pygame.draw.rect(self.image, (50, 200, 50), (1, 12, 28, 4))
            pygame.draw.rect(self.image, RED, (5, 18, 20, 2))
        elif self.type == "pizza":
            # Slice
            points = [(15, 2), (2, 25), (28, 25)]
            pygame.draw.polygon(self.image, (255, 200, 100), points)
            pygame.draw.polygon(self.image, (200, 100, 50), [(2,25), (28,25), (26,28), (4,28)]) # Crust
            # Pepperoni
            pygame.draw.circle(self.image, RED, (15, 12), 3)
            pygame.draw.circle(self.image, RED, (10, 20), 3)
            pygame.draw.circle(self.image, RED, (20, 18), 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
