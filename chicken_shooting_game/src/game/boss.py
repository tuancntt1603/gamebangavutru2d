import pygame
import random
import math
from ..utils.config import GOLD, RED, WHITE, YELLOW, BLACK, SCREEN_WIDTH, BOSS_HP_BASE, CYAN, PURPLE, GREEN, BLUE

class Boss(pygame.sprite.Sprite):
    def __init__(self, level=1, boss_type="regular"):
        super().__init__()
        import os
        self.type = boss_type
        
        # Determine image based on type
        if boss_type == "commando":
            img_name = "boss_commando.png"
            size = (180, 180)
            self.hp = BOSS_HP_BASE * 3.0
        elif boss_type == "blue_vest":
            img_name = "boss_blue_vest.png"
            size = (150, 150)
            self.hp = BOSS_HP_BASE * 1.5
        elif boss_type == "yolk_king":
            img_name = "boss_yolk_king.png"
            size = (200, 200)
            self.hp = BOSS_HP_BASE * 5.0
        elif boss_type == "techno":
            img_name = "boss_techno.png"
            size = (150, 150)
            self.hp = BOSS_HP_BASE * 1.5
        else:
            img_name = "boss.png"
            size = (150, 150)
            self.hp = BOSS_HP_BASE
            
        # Tăng sức mạnh Boss theo chu kỳ Level
        self.hp = int(self.hp * (1.15 ** (level / 5)))
            
        img_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', img_name)
        if os.path.exists(img_path):
            self.base_image = pygame.image.load(img_path).convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, size)
            self.has_loaded_image = True
        else:
            self.base_image = pygame.Surface(size, pygame.SRCALPHA)
            self.has_loaded_image = False
            
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = -size[1]
        self.target_y = 100
        
        self.max_hp = self.hp
        self.speed = 1 + (level * 0.2)
        if boss_type == "techno": self.speed *= 1.5
        
        self.time = 0
        self.laser_active = False
        self.laser_timer = 0
        self.laser_x = 0
        self.draw_boss()

    def draw_boss(self):
        # 1. Base procedural shapes if image is basically empty surface
        if getattr(self, 'has_loaded_image', False):
            self.image = self.base_image.copy()
        else:
            # Clear or prepare surface
            self.image.fill((0,0,0,0))
            
            if self.type == "commando":
                # Camo body with depth
                pygame.draw.ellipse(self.image, (34, 139, 34), (10, 30, 160, 120))
                pygame.draw.ellipse(self.image, (46, 139, 87), (20, 40, 140, 100)) # Highlight
                # Military Cap - Beret
                pygame.draw.ellipse(self.image, (178, 34, 34), (50, 5, 90, 45)) # Red beret
                pygame.draw.rect(self.image, GOLD, (65, 20, 15, 10), border_radius=2) # Emblem
                # Angry eyes
                pygame.draw.circle(self.image, WHITE, (60, 75), 15)
                pygame.draw.circle(self.image, WHITE, (120, 75), 15)
                pygame.draw.circle(self.image, BLACK, (65, 75), 5)
                pygame.draw.circle(self.image, BLACK, (125, 75), 5)
                # Scar
                pygame.draw.line(self.image, (139, 0, 0), (110, 60), (140, 90), 4)
            elif self.type == "blue_vest":
                # Sleek Chicken body
                pygame.draw.ellipse(self.image, WHITE, (25, 25, 120, 120))
                # Blue Vest with detail
                pygame.draw.polygon(self.image, (0, 0, 128), [(30, 60), (140, 60), (120, 130), (50, 130)])
                pygame.draw.line(self.image, CYAN, (35, 80), (135, 80), 2)
                # Pilot Goggles
                pygame.draw.rect(self.image, (50, 50, 50), (45, 50, 80, 25), border_radius=10)
                pygame.draw.rect(self.image, CYAN, (50, 55, 30, 15), border_radius=5)
                pygame.draw.rect(self.image, CYAN, (85, 55, 30, 15), border_radius=5)
            elif self.type == "yolk_king":
                # Red Yolk body (though we have an image now, keep this for safety)
                pygame.draw.ellipse(self.image, (255, 69, 0), (10, 30, 180, 150))
                # Golden Crown
                points = [(60, 35), (80, 10), (100, 35), (120, 10), (140, 35), (140, 55), (60, 55)]
                pygame.draw.polygon(self.image, GOLD, points)
                # Eyes
                pygame.draw.circle(self.image, WHITE, (70, 80), 20)
                pygame.draw.circle(self.image, WHITE, (130, 80), 20)
                pygame.draw.circle(self.image, RED, (70, 80), 8)
                pygame.draw.circle(self.image, RED, (130, 80), 8)
        
        # 2. Outer Glow / Aura (New!)
        glow_size = self.rect.width // 2 + int(math.sin(self.time * 5) * 10)
        glow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.type == "commando": pulse_color = GREEN
        elif self.type == "blue_vest": pulse_color = BLUE
        elif self.type == "yolk_king": pulse_color = RED
        elif self.type == "techno": pulse_color = CYAN
        else: pulse_color = PURPLE
        
        core_color = (*pulse_color, max(0, min(255, 150 + int(math.sin(self.time * 10) * 80))))
        center_x, center_y = self.rect.width // 2, self.rect.height // 2
        pygame.draw.circle(self.image, core_color, (center_x, center_y), self.rect.width // 3, 2)
        
        # Đặc hiệu cho Yolk King (Vương miện lấp lánh)
        if self.type == "yolk_king":
             for i in range(3):
                 sparkle_x = center_x + int(math.cos(self.time * 5 + i) * 80)
                 sparkle_y = center_y - 80 + int(math.sin(self.time * 3 + i) * 20)
                 pygame.draw.circle(self.image, GOLD, (sparkle_x, sparkle_y), 5)
        
        # 2. Laser Indicators
        if self.laser_active:
            if self.laser_timer > 60: # Charging
                charge_alpha = int((120 - self.laser_timer) / 60 * 255)
                # Glow at bottom nozzle
                pygame.draw.circle(self.image, (255, 0, 0, charge_alpha), (center_x, self.rect.height - 20), 15)
            else: # Firing
                # Draw laser on the Boss image? No, let's draw it in the Game draw loop for full screen
                pass

    def update(self):
        self.time += 0.05
        # Enter screen
        if self.rect.y < self.target_y:
            self.rect.y += self.speed
        else:
            # Horizontal movement
            if self.type == "yolk_king":
                self.rect.x = SCREEN_WIDTH // 2 - 100 + int(math.sin(self.time * 0.8) * 450)
                self.rect.y = self.target_y + int(math.sin(self.time * 2) * 50)
            elif self.type == "commando":
                self.rect.x = SCREEN_WIDTH // 2 - 90 + int(math.sin(self.time * 0.5) * 300)
            elif self.type == "blue_vest":
                self.rect.x = SCREEN_WIDTH // 2 - 75 + int(math.sin(self.time * 1.5) * 350)
            else:
                self.rect.x = SCREEN_WIDTH // 2 - 75 + int(math.sin(self.time) * 300)
            
        # Re-draw to animate pulsing cores
        self.draw_boss()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def shoot_spread(self):
        from .egg import Egg
        # Diversified spread patterns
        eggs = []
        if self.type == "commando":
            # Ném lựu đạn (Trứng to, nổ lan)
            for i in range(-120, 121, 60):
                 egg = Egg(self.rect.centerx + i, self.rect.bottom)
                 egg.speed = 5
                 eggs.append(egg)
        elif self.type == "yolk_king":
            # Quyền trượng phép thuật (Đạn tỏa tròn)
            for angle in range(0, 360, 45):
                 rad = math.radians(angle)
                 egg = Egg(self.rect.centerx, self.rect.bottom)
                 egg.speed = 7
                 eggs.append(egg)
        elif self.type == "blue_vest":
            # Standard fast 3-way
            for i in [-50, 0, 50]:
                 egg = Egg(self.rect.centerx + i, self.rect.bottom)
                 egg.speed = 8
                 eggs.append(egg)
        elif self.type == "techno":
            # 5-way fast spread
            for i in [-60, -30, 0, 30, 60]:
                 egg = Egg(self.rect.centerx + i, self.rect.bottom)
                 egg.speed = 9
                 eggs.append(egg)
        else:
            # 3-way standard spread
            for i in [-40, 0, 40]:
                 egg = Egg(self.rect.centerx + i, self.rect.bottom)
                 egg.speed = 6
                 eggs.append(egg)
        return eggs

    def spawn_reinforcements(self):
        from .chicken import Chicken
        # Gà áo xanh triệu hồi đồng bọn
        if self.type == "blue_vest" and random.random() < 0.03:
             c = Chicken(level=1, chicken_type="turbo", 
                         target_x=self.rect.centerx + random.randint(-250, 250),
                         target_y=self.rect.bottom + 80)
             c.state = "SWOOPING"
             return [c]
        return []
