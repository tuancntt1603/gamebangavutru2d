import pygame
from ..utils.config import ORANGE, YELLOW, WHITE

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, btype="Vulcan"):
        super().__init__()
        self.type = btype
        self.angle = 0
        self.pierce = False
        self.hit_targets = set()
        # Color palettes based on type
        if btype == "Vulcan":
            glow, mid, core = (255, 100, 0, 80), (255, 150, 0, 150), (255, 255, 200)
        elif btype == "Ion":
            glow, mid, core = (0, 200, 255, 80), (0, 255, 255, 150), (200, 255, 255)
        elif btype == "Flak":
            glow, mid, core = (50, 255, 50, 80), (100, 255, 100, 150), (200, 255, 200)
        elif btype == "Rocket":
            glow, mid, core = (255, 50, 50, 150), (255, 150, 0, 200), (255, 255, 150)
        elif btype == "Laser":
            glow, mid, core = (255, 50, 50, 150), (255, 100, 100, 200), (255, 200, 200)
        else:
            glow, mid, core = (200, 200, 200, 80), (255, 255, 255, 150), (255, 255, 255)

        if btype == "Rocket":
            self.image = pygame.Surface((30, 60), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.image, glow, [(15, 0), (30, 60), (0, 60)])
            pygame.draw.polygon(self.image, mid, [(15, 10), (25, 60), (5, 60)])
            pygame.draw.line(self.image, core, (15, 20), (15, 60), 6)
            pygame.draw.circle(self.image, WHITE, (15, 20), 4)
            self.speed = -12
            self.damage = 10
        elif btype == "Laser":
            self.image = pygame.Surface((10, 100), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, glow, (0, 0, 10, 100), border_radius=5)
            pygame.draw.rect(self.image, mid, (2, 0, 6, 100), border_radius=3)
            pygame.draw.rect(self.image, core, (4, 0, 2, 100))
            self.speed = -25
            self.damage = 5
            self.pierce = True
        else:
            self.image = pygame.Surface((16, 40), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.image, glow, [(8, 0), (16, 40), (0, 40)])
            pygame.draw.polygon(self.image, mid, [(8, 5), (14, 40), (2, 40)])
            pygame.draw.line(self.image, core, (8, 10), (8, 40), 3)
            pygame.draw.circle(self.image, WHITE, (8, 10), 2)
            self.speed = -18
            self.damage = 1
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        self.active = True

    def update(self, target_pos=None):
        import math
        
        # Simple straight flight for Rockets as requested
        if self.type == "Rocket":
            self.speed = -25 # High speed
            self.damage = 20 # High damage

        # Move with current angle
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y += self.speed * math.cos(rad)
        
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        if self.rect.bottom < 0 or self.rect.top > 900 or self.rect.left < 0 or self.rect.right > 1200:
            self.active = False
            self.kill()
