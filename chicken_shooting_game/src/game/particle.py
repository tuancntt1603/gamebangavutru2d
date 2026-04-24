import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = random.uniform(-5, 5)
        self.vel_y = random.uniform(-5, 5)
        self.life = 30 # Duration in frames

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0:
            self.kill()

class ExplosionHandler:
    def __init__(self, group):
        self.group = group

    def create_explosion(self, x, y, color=(255, 100, 0), count=15):
        for _ in range(count):
            p = Particle(x, y, color)
            self.group.add(p)
