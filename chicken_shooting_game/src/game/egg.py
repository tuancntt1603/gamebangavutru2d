import pygame
from ..utils.config import WHITE, EGG_SPEED

class Egg(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Initial draw: Simple White Oval
        self.image = pygame.Surface((20, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, WHITE, (0, 0, 20, 30))
        # Add subtle shading
        pygame.draw.ellipse(self.image, (220, 220, 220), (3, 3, 14, 24))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = EGG_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 800:
            self.kill()
