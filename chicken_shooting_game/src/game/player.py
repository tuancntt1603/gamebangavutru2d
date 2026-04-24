import pygame
import random
from ..utils.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLUE, YELLOW, ORANGE, RED, CYAN, GREEN
from .bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        import os
        img_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', 'player.png')
        if os.path.exists(img_path):
            self.base_image = pygame.image.load(img_path).convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (60, 60))
        else:
            self.base_image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.image = self.base_image.copy()
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT - 100
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.smooth_x = float(self.rect.centerx)
        self.smooth_y = float(self.rect.centery)
        self.cooldown = 0
        
        # CIU Style Weapon System
        self.weapon_type = "Vulcan" # Vulcan, Ion, Flak, Lightning
        self.weapon_level = 1
        self.max_weapon_level = 20
        self.powerup_timer = 0
        self.fire_rate_multiplier = 1.0
        self.shield_active = False
        self.shield_timer = 0
        self.magnet_timer = 0
        self.speed_timer = 0
        
        self.draw_ship()

    def draw_ship(self):
        # Start fresh with the base image sprite
        if hasattr(self, 'base_image'):
            self.image = self.base_image.copy()
        else:
            self.image.fill((0, 0, 0, 0))
        
        # 6. Combat Mode Highlights (Red for Vulcan, Cyan for Ion, Green for Flak)
        highlight_color = RED if self.weapon_type == "Vulcan" else CYAN if self.weapon_type == "Ion" else GREEN
        if self.weapon_level > 1:
            pygame.draw.rect(self.image, highlight_color, (25, 42, 2, 6))
            pygame.draw.rect(self.image, highlight_color, (33, 42, 2, 6))
        else:
            pygame.draw.rect(self.image, highlight_color, (25, 42, 2, 4))
            pygame.draw.rect(self.image, highlight_color, (33, 42, 2, 4))
        
        # 7. Shield Halo (If Active)
        if self.shield_active:
            shield_color = (100, 200, 255, 120 + random.randint(-40, 40))
            pygame.draw.circle(self.image, shield_color, (30, 30), 30, 2)

    def update(self, hand_x, hand_y):
        # Target position in pixels
        target_x = hand_x * SCREEN_WIDTH
        target_y = hand_y * SCREEN_HEIGHT
        
        # Smooth Interpolation (Lerp factor: 0.2 for that fluid CIU feel)
        lerp_factor = 0.5 if self.speed_timer > 0 else 0.2
        self.smooth_x += (target_x - self.smooth_x) * lerp_factor
        self.smooth_y += (target_y - self.smooth_y) * lerp_factor
        
        # Update rect position with boundaries
        self.rect.centerx = max(30, min(SCREEN_WIDTH - 30, int(self.smooth_x)))
        self.rect.centery = max(30, min(SCREEN_HEIGHT - 30, int(self.smooth_y)))
        self.x = self.rect.centerx
        self.y = self.rect.centery
        
        # Update power-up timers
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer == 0:
                self.fire_rate_multiplier = 1.0
                
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield_active = False
                
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
            
        if self.speed_timer > 0:
            self.speed_timer -= 1

        if self.cooldown > 0:
            self.cooldown -= 1
            
        # Optional: Re-draw glow to animate
        if random.random() > 0.5:
             self.draw_ship() # Pulse effect

    def shoot(self):
        if self.cooldown == 0:
            # Multiplier affects cooldown (smaller = faster)
            self.cooldown = int(8 / self.fire_rate_multiplier)
            
            bullets = []
            if self.weapon_type == "Vulcan":
                # Vulcan shot: Multi-stream straight
                if self.weapon_level == 1:
                    bullets.append(Bullet(self.rect.centerx, self.rect.top, "Vulcan"))
                elif self.weapon_level == 2:
                    bullets.append(Bullet(self.rect.centerx - 10, self.rect.top, "Vulcan"))
                    bullets.append(Bullet(self.rect.centerx + 10, self.rect.top, "Vulcan"))
                elif self.weapon_level >= 3:
                    bullets.append(Bullet(self.rect.centerx, self.rect.top, "Vulcan"))
                    bullets.append(Bullet(self.rect.centerx - 20, self.rect.top + 10, "Vulcan"))
                    bullets.append(Bullet(self.rect.centerx + 20, self.rect.top + 10, "Vulcan"))
            
            elif self.weapon_type == "Ion":
                # Ion shot: Fast vertical laser-like bullets
                bullets.append(Bullet(self.rect.centerx, self.rect.top, "Ion"))
                if self.weapon_level >= 2:
                    bullets.append(Bullet(self.rect.centerx, self.rect.top - 20, "Ion"))
            
            elif self.weapon_type == "Flak":
                # Flak shot: Spread pattern
                bullets.append(Bullet(self.rect.centerx, self.rect.top, "Flak"))
                if self.weapon_level >= 2:
                    b1 = Bullet(self.rect.centerx, self.rect.top, "Flak")
                    b1.angle = -10
                    b2 = Bullet(self.rect.centerx, self.rect.top, "Flak")
                    b2.angle = 10
                    bullets.extend([b1, b2])

            elif self.weapon_type == "Spread":
                bullets.append(Bullet(self.rect.centerx, self.rect.top, "Ion"))
                b1 = Bullet(self.rect.centerx, self.rect.top, "Ion")
                b1.angle = -15
                b2 = Bullet(self.rect.centerx, self.rect.top, "Ion")
                b2.angle = 15
                bullets.extend([b1, b2])
                
                if self.weapon_level >= 3:
                    b3 = Bullet(self.rect.centerx, self.rect.top, "Ion")
                    b3.angle = -30
                    b4 = Bullet(self.rect.centerx, self.rect.top, "Ion")
                    b4.angle = 30
                    bullets.extend([b3, b4])
                    
            elif self.weapon_type == "Laser":
                bullets.append(Bullet(self.rect.centerx, self.rect.top, "Laser"))

            return bullets
        return None

    def apply_powerup(self, ptype):
        if ptype == "shield":
             self.shield_active = True
             self.shield_timer = 300
             return "shield_applied"
             
        if ptype == "upgrade":
             if self.weapon_level < self.max_weapon_level:
                 self.weapon_level += 1
             # Upgrade also gives temporary rapid fire
             self.fire_rate_multiplier = 1.5 + (self.weapon_level * 0.1)
             self.powerup_timer = 600
             return "weapon_upgraded"
             
        if ptype in ["spread", "laser"]:
             new_type = ptype.capitalize()
             if self.weapon_type != new_type:
                 self.weapon_type = new_type
                 self.weapon_level = 1
             else:
                 if self.weapon_level < self.max_weapon_level:
                     self.weapon_level += 1
             return "weapon_changed"
             
        if ptype == "magnet":
             self.magnet_timer = 600 # 10 seconds
             return "magnet_applied"
             
        if ptype == "speed":
             self.speed_timer = 300 # 5 seconds
             return "speed_applied"
             
        return ptype # Unhandled by player, handle in Game
