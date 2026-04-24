import pygame
from src.game.player import Player
from src.game.chicken import Chicken, Formation
from src.game.bullet import Bullet
from src.game.boss import Boss
from src.game.egg import Egg
from src.game.food import Food
from src.game.powerup import PowerUp
from src.game.particle import Particle, ExplosionHandler
from src.utils.config import SCREEN_WIDTH, SCREEN_HEIGHT, CHICKENS_PER_LEVEL, BOSS_LEVEL_1, BOSS_LEVEL_2, RED, WHITE, YELLOW, BLUE, CYAN, GOLD, MAX_HP, GREEN, PURPLE, ORANGE
from src.utils.leaderboard import load_leaderboard, save_score
from src.utils.audio_manager import AudioManager

import os
import math
import random

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Chicken Shooting Game")

        # Load background
        bg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', 'background_premium.png')
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.background = None
            
        self.bg_y = 0
        
        self.sound_enabled = True
        self.high_graphics = True
        self.menu_debounce = 0

        self.player = Player()
        self.chickens = []
        self.bullets = []
        self.boss = None

        self.level = 1
        self.wave = 1
        self.score = 0
        self.kills_in_level = 0
        self.player_hp = MAX_HP
        self.invincible_timer = 0
        self.state = "INTRO_LOGO" # INTRO_LOGO, INTRO_STORY, STARTING, PLAYING...
        self.timer = 0
        self.intro_phase = 0
        self.fade_alpha = 0
        self.story_y = SCREEN_HEIGHT
        self.ship_intro_y = SCREEN_HEIGHT + 100
        self.hyperspace_timer = 0
        self.logo_scale = 0.5
        self.thruster_particles = []
        
        # Parallax Space environment (x, y, speed, size)
        self.stars = []
        for _ in range(150):
            layer = random.choice([1, 2, 3])
            speed = layer * 0.5 + random.uniform(0, 0.5)
            size = layer
            self.stars.append([random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), speed, size])
            
        self.leaderboard = load_leaderboard()
        self.score_saved = False
        self.player_name = ""
        self.name_timer = 0
        self.eggs = []
        self.foods = []
        self.powerups = []
        self.particles = pygame.sprite.Group()
        self.explosions = ExplosionHandler(self.particles)
        
        self.shake_amount = 0
        self.slow_mo = False
        self.freeze_timer = 0
        self.rocket_cooldown = 0
        self.rocket_count = 3
        self.bomb_count = 1
        self.prev_five_fingers = False
        self.is_victory = False
        try:
            self.font = pygame.font.SysFont("segoeui", 30, bold=True)
            self.big_font = pygame.font.SysFont("segoeui", 70, bold=True)
        except:
            self.font = pygame.font.Font(None, 36)
            self.big_font = pygame.font.Font(None, 74)

        # Audio Setup
        self.audio_manager = AudioManager()

    def spawn_initial_wave(self):
        self.chickens = []
        self.wave = 1
        self.boss = None
        self.chickens = Formation.get_wave(self.level, self.wave)

    def next_level(self):
        if self.level < 10:
            self.level += 1
            self.wave = 1
            self.kills_in_level = 0
            self.state = "LEVEL_TIMEOUT"
            self.timer = 120 # 2 seconds of transition
        else:
            self.state = "SAVE_SCORE"
            self.is_victory = True
            if self.sound_enabled:
                self.audio_manager.play("powerup")

    def transition_update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.state = "PLAYING"
            self.spawn_initial_wave()

    def update(self, gestures, events=[]):
        if self.menu_debounce > 0:
            self.menu_debounce -= 1
        
        if self.state == "SAVE_SCORE":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.player_name.strip() == "":
                             self.player_name = "Elite Pilot"
                        self.leaderboard = save_score(self.score, self.player_name)
                        self.score_saved = True
                        self.state = "GAMEOVER"
                    else:
                        if len(self.player_name) < 12 and event.unicode.isprintable():
                             self.player_name += event.unicode
            return

        if self.state == "STARTING":
             self.player.update(gestures.get("x", 0.5), gestures.get("y", 0.5))
             
             bx = SCREEN_WIDTH // 2 - 200
             by = SCREEN_HEIGHT // 2
             r_start = pygame.Rect(bx, by, 400, 60)
             cursor_rect = pygame.Rect(self.player.x - 5, self.player.y - 5, 10, 10)
             
             keys = pygame.key.get_pressed()
             # Cho phép bấm phím Space/Enter để bắt đầu chơi luôn mà không cần ngắm chuột
             if (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]) and self.menu_debounce == 0:
                 self.state = "PLAYING"
                 self.menu_debounce = 30
                 self.spawn_initial_wave()
                 return
                 
             is_click = gestures.get("shoot", False) or pygame.mouse.get_pressed()[0]
             
             if is_click and self.menu_debounce == 0:
                 if r_start.colliderect(cursor_rect) or r_start.collidepoint(pygame.mouse.get_pos()):
                     self.state = "PLAYING"
                     self.menu_debounce = 30
                     self.spawn_initial_wave()
             return

        if self.state == "INTRO_LOGO":
            self.timer += 1
            if self.timer == 1 and self.sound_enabled:
                self.audio_manager.play("intro")
            
            # Fade and scale logo
            if self.timer < 60: self.fade_alpha = min(255, self.fade_alpha + 5)
            elif self.timer > 120: self.fade_alpha = max(0, self.fade_alpha - 5)
            self.logo_scale += 0.003
            
            if self.timer > 180 or pygame.key.get_pressed()[pygame.K_SPACE]:
                self.state = "INTRO_STORY"
                self.timer = 0
                self.fade_alpha = 0
            return

        if self.state == "INTRO_STORY":
            self.timer += 1
            # Update parallax space background
            for i in range(len(self.stars)):
                x, y, speed, size = self.stars[i]
                y = (y + speed) % SCREEN_HEIGHT
                self.stars[i] = [x, y, speed, size]

            # Ship fly-in and thrusters
            if self.ship_intro_y > SCREEN_HEIGHT // 2 + 150:
                self.ship_intro_y -= 1.5
            
            # Emit thruster particles
            if self.timer % 2 == 0:
                px = SCREEN_WIDTH // 2 + random.randint(-10, 10)
                py = self.ship_intro_y + 30
                self.thruster_particles.append([px, py, random.uniform(-0.5, 0.5), random.uniform(2, 5), 255])
            
            # Update particles
            for pt in self.thruster_particles:
                pt[0] += pt[2]
                pt[1] += pt[3]
                pt[4] -= 10
            self.thruster_particles = [pt for pt in self.thruster_particles if pt[4] > 0]
            
            # Story text scrolling
            self.story_y -= 0.8
            
            if self.timer > 900 or pygame.key.get_pressed()[pygame.K_SPACE]:
                self.state = "INTRO_HYPERSPACE"
                if self.sound_enabled: 
                    self.audio_manager.fadeout("intro", 1000)
                    self.audio_manager.play("rocket")
                self.timer = 0
            return
            
        if self.state == "INTRO_HYPERSPACE":
            # Hyperspace warp effect
            self.hyperspace_timer += 1
            
            # Extremely fast stars
            for i in range(len(self.stars)):
                x, y, speed, size = self.stars[i]
                y = (y + speed * 20) % SCREEN_HEIGHT
                self.stars[i] = [x, y, speed, size]
                
            if self.hyperspace_timer > 60: # 1 second of warp
                self.state = "STARTING"
                self.menu_debounce = 30
            return

        if self.state == "LEVEL_TIMEOUT":
            self.transition_update()
            self.player.update(gestures.get("x", 0.5), gestures.get("y", 0.5))
            return

        if self.state == "WIN" or self.state == "GAMEOVER":
             self.player.update(gestures.get("x", 0.5), gestures.get("y", 0.5))
             
             for event in events:
                 if event.type == pygame.KEYDOWN:
                     if event.key == pygame.K_r:
                         self.__init__()
                     elif event.key == pygame.K_ESCAPE:
                         pygame.quit()
                         import sys
                         sys.exit()
                 
                 if event.type == pygame.MOUSEBUTTONDOWN:
                     mx, my = pygame.mouse.get_pos()
                     # Check buttons (positions defined in draw_scene)
                     bx, by = SCREEN_WIDTH//2 - 210, SCREEN_HEIGHT - 150
                     if pygame.Rect(bx, by, 200, 50).collidepoint(mx, my):
                         self.__init__()
                     elif pygame.Rect(bx + 220, by, 200, 50).collidepoint(mx, my):
                         pygame.quit()
                         import sys
                         sys.exit()
             return

        # SLOW MOTION GESTURE (2 Hands)
        if gestures.get("hands", 0) >= 2:
            self.slow_mo = True
        else:
            self.slow_mo = False
        
        current_five = gestures.get("five_fingers", False)
        
        # ROCKET GESTURE (5 ngón) - Yêu cầu khép tay lại mới được giơ tiếp
        if current_five and not self.prev_five_fingers and self.rocket_cooldown == 0 and self.rocket_count > 0:
            self.trigger_rocket()
            
        self.prev_five_fingers = current_five
            
        # BOMB GESTURE (Fist)
        if gestures.get("fist", False) and self.bomb_count > 0:
            self.trigger_bomb()

        if self.rocket_cooldown > 0: self.rocket_cooldown -= 1

        if getattr(self, 'freeze_timer', 0) > 0:
            self.freeze_timer -= 1
            dt = 0.0 # Freeze chickens!
        else:
            dt = 0.3 if self.slow_mo else 1.0

        x = gestures.get("x", 0.5)
        y = gestures.get("y", 0.5)
        
        # Cho phép bấm Chuột trái hoặc Phím Space để bắn (Dự phòng cho Hand-tracking)
        keys = pygame.key.get_pressed()
        shoot = gestures.get("shoot", False) or keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
        
        self.player.update(x, y)
        
        # bắn đạn
        if shoot:
            new_bullets = self.player.shoot()
            if new_bullets:
                self.bullets.extend(new_bullets)
                if self.sound_enabled:
                    self.audio_manager.play("laser")

        # cập nhật đạn
        for bullet in self.bullets:
            bullet.update()
            
            # Rocket specific effects
            if bullet.type == "Rocket" and bullet.active:
                # Smoke trail
                if random.random() < 0.5:
                    self.explosions.create_explosion(bullet.x, bullet.y + 30, (200, 200, 200), 2)
        
        self.bullets = [b for b in self.bullets if b.active]

        # cập nhật trứng
        for egg in self.eggs:
            egg.rect.y += (egg.speed * dt)
            if egg.rect.top > SCREEN_HEIGHT: egg.kill()
        self.eggs = [e for e in self.eggs if e.rect.top <= SCREEN_HEIGHT]

        # Magnet pull logic
        if getattr(self.player, 'magnet_timer', 0) > 0:
            for item in self.foods + self.powerups:
                dx = self.player.rect.centerx - item.rect.centerx
                dy = self.player.rect.centery - item.rect.centery
                dist = math.hypot(dx, dy)
                if 0 < dist < 400: # 400px magnet radius
                    speed_pull = 15 * dt
                    item.rect.x += int(dx / dist * speed_pull)
                    item.rect.y += int(dy / dist * speed_pull)

        # cập nhật food & powerups
        for item in self.foods + self.powerups:
            item.rect.y += (item.speed * dt)
        self.foods = [f for f in self.foods if f.rect.top < SCREEN_HEIGHT]
        self.powerups = [p for p in self.powerups if p.rect.top < SCREEN_HEIGHT]

        # cập nhật particles
        self.particles.update()

        # Bất tử tạm thời
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        if self.shake_amount > 0:
            self.shake_amount -= 1

        # Kiểm tra va chạm người chơi - vật phẩm
        for f in self.foods[:]:
            if self.player.rect.colliderect(f.rect):
                self.score += getattr(f, 'score', 50)
                self.foods.remove(f)
        for p in self.powerups[:]:
            if self.player.rect.colliderect(p.rect):
                if self.sound_enabled:
                    self.audio_manager.play("powerup")
                effect = self.player.apply_powerup(p.type)
                if effect == "health":
                    self.player_hp = min(MAX_HP, self.player_hp + 1)
                elif effect == "rocket":
                    self.rocket_count += 1
                elif effect == "bomb" or effect == "nuke":
                    self.trigger_bomb()
                elif effect == "coin":
                    self.score += 500
                elif effect == "freeze":
                    self.freeze_timer = 300 # Freeze for frames
                self.score += 100
                self.powerups.remove(p)

        # Kiểm tra va chạm người chơi - trứng/gà
        if self.invincible_timer == 0 and self.state in ["PLAYING", "BOSS"]:
            # Va chạm với trứng
            for egg in self.eggs:
                if self.player.rect.colliderect(egg.rect):
                    if getattr(self.player, "shield_active", False):
                        egg.kill()
                        self.explosions.create_explosion(egg.rect.centerx, egg.rect.centery, CYAN, 5)
                        continue
                    self.hit_player()
                    egg.kill()
                    break
            
            # Va chạm trực tiếp với gà
            for chicken in self.chickens:
                if getattr(chicken, "hp", 1) <= 0: continue
                if self.player.rect.colliderect(chicken.rect):
                    if getattr(self.player, "shield_active", False):
                        chicken.hp = 0
                        self.explosions.create_explosion(chicken.x, chicken.y, chicken.color)
                        continue
                    self.hit_player()
                    self.explosions.create_explosion(chicken.x, chicken.y, chicken.color)
                    if self.sound_enabled: self.audio_manager.play("explosion")
                    chicken.hp = 0
                    break

        if self.state == "BOSS" and self.boss:
            self.boss.update()
            # Boss bắn trứng
            if pygame.time.get_ticks() % 60 == 0:
                new_eggs = self.boss.shoot_spread()
                self.eggs.extend(new_eggs)
            
            # Additional logic for reinforcements (Mother Hen)
            new_mini_chickens = self.boss.spawn_reinforcements()
            if new_mini_chickens:
                self.chickens.extend(new_mini_chickens)

            # Boss Laser Collision
            if self.boss.laser_active and self.boss.laser_timer <= 60:
                # Laser is firing
                laser_rect = pygame.Rect(self.boss.rect.centerx - 10, self.boss.rect.bottom, 20, SCREEN_HEIGHT)
                if self.player.rect.colliderect(laser_rect) and self.invincible_timer == 0:
                    if not getattr(self.player, "shield_active", False):
                        self.hit_player()

            # Check player hits boss
            for bullet in self.bullets:
                if not bullet.active: continue
                if self.boss.rect.collidepoint(bullet.x, bullet.y):
                    if getattr(bullet, "pierce", False):
                        if self.boss in bullet.hit_targets:
                            continue
                        bullet.hit_targets.add(self.boss)
                    else:
                        bullet.active = False
                        
                    damage_dealt = getattr(bullet, "damage", 1)
                    if getattr(bullet, "type", "Vulcan") == "Rocket":
                        self.explosions.create_explosion(bullet.x, bullet.y, RED, 50)
                        self.shake_amount = 30
                        # Area damage to regular chickens
                        for c in self.chickens:
                            dist = math.hypot(c.rect.centerx - bullet.x, c.rect.centery - bullet.y)
                            if dist < 200:
                                c.hp = 0 # Instant kill regular chickens in range
                        if self.sound_enabled: self.audio_manager.play("explosion")
                    else:
                        self.explosions.create_explosion(bullet.x, bullet.y, WHITE, 3)
                        
                    if self.sound_enabled:
                        self.audio_manager.play("explosion", volume=0.1)
                        
                    if self.boss.take_damage(damage_dealt):
                        self.score += 1000
                        self.explosions.create_explosion(self.boss.rect.centerx, self.boss.rect.centery, GOLD, 50)
                        self.boss = None
                        self.next_level()
                        break
        elif self.state == "PLAYING":
            # Update chickens with new state machine
            for chicken in self.chickens:
                chicken.update(dt, self.player.rect.centerx)
                
                # Gà đẻ trứng (chance handled inside try_drop_egg)
                if chicken.state == "HOVERING":
                    new_egg = chicken.try_drop_egg()
                    if new_egg: self.eggs.append(new_egg)

                # kiểm tra trúng
                for bullet in self.bullets:
                    if not bullet.active: continue
                    if getattr(chicken, "hp", 1) <= 0: continue
                    
                    if abs(bullet.x - (chicken.rect.x + 30)) < 35 and abs(bullet.y - (chicken.rect.y + 30)) < 35:
                        if getattr(bullet, "pierce", False):
                            if chicken in bullet.hit_targets:
                                continue
                            bullet.hit_targets.add(chicken)
                            
                        chicken.hp -= getattr(bullet, "damage", 1)
                        if getattr(bullet, "type", "Vulcan") == "Rocket":
                            self.explosions.create_explosion(bullet.x, bullet.y, RED, 40)
                            self.shake_amount = 20
                            bullet.active = False
                            if self.sound_enabled: self.audio_manager.play("explosion")
                            # Clear nearby chickens
                            for c in self.chickens:
                                if c != chicken and math.hypot(c.rect.centerx - bullet.x, c.rect.centery - bullet.y) < 150:
                                    c.hp = 0
                        elif not getattr(bullet, "pierce", False):
                            bullet.active = False
                        
                        if chicken.hp <= 0:
                            self.score += 10
                            self.kills_in_level += 1
                            self.explosions.create_explosion(chicken.rect.centerx, chicken.rect.centery, YELLOW)
                            if self.sound_enabled: self.audio_manager.play("explosion")
                            self.shake_amount = 5
                            
                            # Loot drop
                            loot = chicken.try_drop_loot()
                            if isinstance(loot, Food): self.foods.append(loot)
                            if isinstance(loot, PowerUp): self.powerups.append(loot)
                        break
            
            # Remove dead chickens
            self.chickens = [c for c in self.chickens if getattr(c, "hp", 1) > 0]
            
            # Check wave clear
            if len(self.chickens) == 0 and self.state == "PLAYING":
                self.wave += 1
                if self.wave <= 3:
                    self.chickens = Formation.get_wave(self.level, self.wave)
                elif self.wave == 4:
                    self.state = "BOSS"
                    boss_pool = ["commando", "blue_vest", "techno", "regular"]
                    b_idx = (self.level - 1) % len(boss_pool)
                    if self.level % 10 == 0:
                        self.boss = Boss(level=self.level, boss_type="yolk_king")
                    else:
                        self.boss = Boss(level=self.level, boss_type=boss_pool[b_idx])

    def hit_player(self):
        self.player_hp -= 1
        self.invincible_timer = 60
        self.shake_amount = 20
        if self.sound_enabled: self.audio_manager.play("hit")
        if self.player_hp <= 0:
            if self.sound_enabled: self.audio_manager.play("game_over")
            self.state = "SAVE_SCORE"

    def trigger_rocket(self):
        self.rocket_count -= 1
        self.rocket_cooldown = 60 # 1 second cooldown
        self.shake_amount = 10
        if self.sound_enabled: self.audio_manager.play("rocket")
        
        rocket = Bullet(self.player.rect.centerx, self.player.rect.top, "Rocket")
        self.bullets.append(rocket)

    def trigger_bomb(self):
        self.bomb_count -= 1
        self.shake_amount = 40
        if self.sound_enabled: self.audio_manager.play("explosion")
        # Clear eggs and nearby chickens
        self.eggs = []
        for chicken in self.chickens:
             if self.player.rect.colliderect(chicken.rect.inflate(400, 400)):
                 self.explosions.create_explosion(chicken.rect.centerx, chicken.rect.centery, RED, 15)
                 chicken.hp = 0
                 self.score += 10
    
    def draw_scene(self, gestures=None):
        # Calculate screen shake offset
        offset_x = random.randint(-self.shake_amount, self.shake_amount)
        offset_y = random.randint(-self.shake_amount, self.shake_amount)
        
        draw_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.background and self.high_graphics:
            # CIU Scrolling space effect
            self.bg_y = (self.bg_y + 2) % SCREEN_HEIGHT
            draw_surf.blit(self.background, (0, self.bg_y))
            draw_surf.blit(self.background, (0, self.bg_y - SCREEN_HEIGHT))
        else:
            draw_surf.fill((0, 0, 0))

        # PiP
        if gestures and gestures.get("cam"):
            cam_surface = gestures["cam"]
            draw_surf.blit(cam_surface, (SCREEN_WIDTH - 170, 10))
            pygame.draw.rect(draw_surf, CYAN, (SCREEN_WIDTH - 171, 9, 162, 122), 1)

        # Draw Entities
        if not (self.invincible_timer > 0 and (pygame.time.get_ticks() // 100) % 2 == 0):
            draw_surf.blit(self.player.image, self.player.rect)

        if self.state == "BOSS" and self.boss:
            # Draw Boss Laser
            if self.boss.laser_active:
                lx = self.boss.rect.centerx
                if self.boss.laser_timer > 60:
                    pygame.draw.line(draw_surf, (255, 0, 0), (lx, self.boss.rect.bottom), (lx, SCREEN_HEIGHT), 2)
                else:
                    pygame.draw.rect(draw_surf, (255, 50, 50, 100), (lx - 20, self.boss.rect.bottom, 40, SCREEN_HEIGHT))
                    pygame.draw.rect(draw_surf, WHITE, (lx - 8, self.boss.rect.bottom, 16, SCREEN_HEIGHT))
            draw_surf.blit(self.boss.image, self.boss.rect)
        else:
            for chicken in self.chickens:
                draw_surf.blit(chicken.image, chicken.rect)

        for b in self.bullets: draw_surf.blit(b.image, b.rect)
        for e in self.eggs: draw_surf.blit(e.image, e.rect)
        for f in self.foods: draw_surf.blit(f.image, f.rect)
        for p in self.powerups: draw_surf.blit(p.image, p.rect)
        
        if self.high_graphics:
            self.particles.draw(draw_surf)

        # HUD
        self.draw_hud(draw_surf)

        if self.state == "INTRO_LOGO":
            logo_text = self.big_font.render("ANTIGRAVITY STUDIOS", True, WHITE)
            # Scale effect
            scaled_logo = pygame.transform.rotozoom(logo_text, 0, self.logo_scale)
            logo_surf = pygame.Surface(scaled_logo.get_size(), pygame.SRCALPHA)
            logo_surf.blit(scaled_logo, (0, 0))
            logo_surf.set_alpha(self.fade_alpha)
            draw_surf.blit(logo_surf, (SCREEN_WIDTH//2 - scaled_logo.get_width()//2, SCREEN_HEIGHT//2 - scaled_logo.get_height()//2))
            
        elif self.state in ["INTRO_STORY", "INTRO_HYPERSPACE"]:
            # Draw Parallax Stars
            for x, y, speed, size in self.stars:
                if self.state == "INTRO_HYPERSPACE":
                    # Draw stars as stretched lines for warp effect
                    pygame.draw.line(draw_surf, WHITE, (int(x), int(y)), (int(x), int(y + speed * 15)), size)
                else:
                    color = (200, 200, 255) if size > 1 else (100, 100, 150)
                    pygame.draw.circle(draw_surf, color, (int(x), int(y)), int(size))
            
            if self.state == "INTRO_STORY":
                # Draw Thruster Particles
                for px, py, vx, vy, alpha in self.thruster_particles:
                    p_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
                    color = (255, 100, 0, int(alpha)) if alpha > 150 else (200, 200, 200, int(alpha))
                    pygame.draw.circle(p_surf, color, (5, 5), 4)
                    draw_surf.blit(p_surf, (int(px) - 5, int(py) - 5))

                # Draw Ship
                ship_rect = self.player.image.get_rect(center=(SCREEN_WIDTH//2, self.ship_intro_y))
                draw_surf.blit(self.player.image, ship_rect)
                
                # Draw Scrolling Story Text (Star Wars style vertical scroll)
                story_lines = [
                    "Năm 3026...",
                    "",
                    "Đội quân gà ngoài hành tinh đã quay trở lại...",
                    "Chúng muốn thống trị Trái Đất...",
                    "",
                    "Bạn là phi công cuối cùng có thể ngăn chặn chúng...",
                    "Hãy sẵn sàng chiến đấu!"
                ]
                
                for i, line in enumerate(story_lines):
                    if not line: continue
                    color = GOLD if "sẵn sàng" in line else CYAN
                    text = self.font.render(line, True, color)
                    
                    y_pos = self.story_y + i * 50
                    
                    # Fade out at the top
                    alpha = 255
                    if y_pos < 200:
                        alpha = max(0, int((y_pos / 200) * 255))
                    elif y_pos > SCREEN_HEIGHT - 100:
                        alpha = max(0, int(((SCREEN_HEIGHT - y_pos) / 100) * 255))
                        
                    if alpha > 0:
                        text_surf = pygame.Surface(text.get_size(), pygame.SRCALPHA)
                        text_surf.blit(text, (0, 0))
                        text_surf.set_alpha(alpha)
                        draw_surf.blit(text_surf, (SCREEN_WIDTH//2 - text.get_width()//2, int(y_pos)))
                    
                skip_text = self.font.render("Press SPACE to Skip", True, (150, 150, 150))
                draw_surf.blit(skip_text, (SCREEN_WIDTH//2 - skip_text.get_width()//2, SCREEN_HEIGHT - 50))

        elif self.state == "STARTING":
            def draw_check(surf, x, y):
                pygame.draw.line(surf, WHITE, (x, y + 15), (x + 10, y + 25), 5)
                pygame.draw.line(surf, WHITE, (x + 10, y + 25), (x + 30, y - 5), 5)

            ts_x, ts_y = SCREEN_WIDTH//2, 120
            
            # Title 1
            title1 = self.big_font.render("CHICKEN", True, WHITE)
            title1_glow = self.big_font.render("CHICKEN", True, BLUE)
            for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (0,-3), (0,3), (-3,0), (3,0)]:
                draw_surf.blit(title1_glow, (ts_x - title1_glow.get_width()//2 + dx, ts_y + dy))
            draw_surf.blit(title1, (ts_x - title1.get_width()//2, ts_y))
            
            # Title 2
            ts_y += 60
            title2 = self.big_font.render("INVADERS", True, WHITE)
            title2_glow = self.big_font.render("INVADERS", True, BLUE)
            for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (0,-3), (0,3), (-3,0), (3,0)]:
                draw_surf.blit(title2_glow, (ts_x - title2_glow.get_width()//2 + dx, ts_y + dy))
            draw_surf.blit(title2, (ts_x - title2.get_width()//2, ts_y))
            
            # Title 3 (Subtitle)
            ts_y += 70
            title3 = self.font.render("REVENGE OF THE YOLK", True, CYAN)
            draw_surf.blit(title3, (ts_x - title3.get_width()//2, ts_y))
            
            # Buttons bounds
            bx, by = SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50
            
            def draw_btn(text, bx, by, checked=None):
                pygame.draw.rect(draw_surf, BLUE, (bx-4, by-4, 408, 68), border_radius=30)
                pygame.draw.rect(draw_surf, CYAN, (bx-2, by-2, 404, 64), border_radius=30)
                pygame.draw.rect(draw_surf, (10, 30, 80), (bx, by, 400, 60), border_radius=30)
                t_surf = self.font.render(text, True, WHITE)
                draw_surf.blit(t_surf, (bx + 200 - t_surf.get_width()//2, by + 15))
            
            draw_btn("Chơi mới!", bx, by)
            
            # Draw cursor for menu interact
            cursor_color = YELLOW if self.menu_debounce > 0 else CYAN
            cursor_pos = (int(self.player.x), int(self.player.y))
            pygame.draw.circle(draw_surf, cursor_color, cursor_pos, 8, 2)
            pygame.draw.line(draw_surf, cursor_color, (cursor_pos[0]-15, cursor_pos[1]), (cursor_pos[0]+15, cursor_pos[1]), 2)
            pygame.draw.line(draw_surf, cursor_color, (cursor_pos[0], cursor_pos[1]-15), (cursor_pos[0], cursor_pos[1]+15), 2)
            
        elif self.state == "WIN":
            # Fallback win screen (normally goes to SAVE_SCORE -> GAMEOVER)
            overlay = self.big_font.render("MISSION ACCOMPLISHED!", True, GOLD)
            draw_surf.blit(overlay, (SCREEN_WIDTH//2 - overlay.get_width()//2, SCREEN_HEIGHT//2 - 50))
        elif self.state == "SAVE_SCORE":
            # Semi-transparent dark overlay
            dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 200))
            draw_surf.blit(dark_overlay, (0, 0))

            title = self.big_font.render("BẠN ĐÃ TỬ TRẬN!", True, RED)
            prompt = self.font.render("NHẬP TÊN PHI CÔNG CỦA BẠN:", True, WHITE)
            
            # Name input field with blinking cursor
            self.name_timer = (self.name_timer + 1) % 60
            cursor = "_" if self.name_timer < 30 else ""
            name_text = self.big_font.render(self.player_name + cursor, True, YELLOW)
            
            instr = self.font.render("Nhấn ENTER để lưu điểm", True, CYAN)

            draw_surf.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            draw_surf.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 300))
            draw_surf.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, 380))
            draw_surf.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 500))

        elif self.state == "GAMEOVER":
            # Show score once already saved
            # Semi-transparent dark overlay
            dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 220))
            draw_surf.blit(dark_overlay, (0, 0))
            
            if getattr(self, "is_victory", False):
                title_text = "VICTORY!"
                title_color = GOLD
                # Fireworks effect
                if random.random() < 0.15:
                    fx = random.randint(100, SCREEN_WIDTH - 100)
                    fy = random.randint(100, SCREEN_HEIGHT - 300)
                    fc = random.choice([GOLD, CYAN, RED, YELLOW, WHITE, GREEN, PURPLE])
                    self.explosions.create_explosion(fx, fy, fc, random.randint(15, 40))
            else:
                title_text = "TRẬN CHIẾN KẾT THÚC"
                title_color = RED

            overlay = self.big_font.render(title_text, True, title_color)
            score_final = self.font.render(f"PHI CÔNG: {self.player_name} - SCORE: {self.score}", True, WHITE)
            
            draw_surf.blit(overlay, (SCREEN_WIDTH//2 - overlay.get_width()//2, 80))
            draw_surf.blit(score_final, (SCREEN_WIDTH//2 - score_final.get_width()//2, 160))
            
            # Draw Leaderboard
            lh_text = self.font.render("--- HALL OF FAME ---", True, GOLD)
            draw_surf.blit(lh_text, (SCREEN_WIDTH//2 - lh_text.get_width()//2, 220))
            
            for i, entry in enumerate(self.leaderboard[:7]): # Show top 7
                entry_text = self.font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, CYAN if i == 0 else WHITE)
                draw_surf.blit(entry_text, (SCREEN_WIDTH//2 - entry_text.get_width()//2, 270 + i * 35))

            # Buttons
            bx, by = SCREEN_WIDTH//2 - 210, SCREEN_HEIGHT - 150
            
            # Draw Restart Button
            pygame.draw.rect(draw_surf, BLUE, (bx, by, 200, 50), border_radius=10)
            t_restart = self.font.render("RESTART (R)", True, WHITE)
            draw_surf.blit(t_restart, (bx + 100 - t_restart.get_width()//2, by + 10))
            
            # Draw Exit Button
            pygame.draw.rect(draw_surf, RED, (bx + 220, by, 200, 50), border_radius=10)
            t_exit = self.font.render("EXIT (ESC)", True, WHITE)
            draw_surf.blit(t_exit, (bx + 320 - t_exit.get_width()//2, by + 10))

        if self.slow_mo:
            slow_text = self.font.render("--- SLOW MOTION ---", True, CYAN)
            draw_surf.blit(slow_text, (SCREEN_WIDTH//2 - slow_text.get_width()//2, SCREEN_HEIGHT - 100))

        # Final screen blit with shake
        self.screen.blit(draw_surf, (offset_x, offset_y))
        pygame.display.update()

    def draw_hud(self, surf):
        # HP
        for i in range(MAX_HP):
            color = RED if i < self.player_hp else (50, 50, 50)
            pygame.draw.circle(surf, color, (30 + i * 35, SCREEN_HEIGHT - 30), 12)
        
        # Weapon Level
        w_text = self.font.render(f"WEAPON: {self.player.weapon_type} LV.{self.player.weapon_level}", True, GREEN)
        surf.blit(w_text, (10, SCREEN_HEIGHT - 70))
        
        # Score
        s_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        surf.blit(s_text, (10, 10))
        
        # Rocket Count and Cooldown
        r_color = ORANGE if self.rocket_count > 0 and self.rocket_cooldown == 0 else (100, 100, 100)
        pygame.draw.rect(surf, (50, 50, 50), (10, 100, 200, 10))
        if self.rocket_cooldown > 0:
            charge_w = 200 * (1 - self.rocket_cooldown / 60)
            pygame.draw.rect(surf, r_color, (10, 100, charge_w, 10))
        elif self.rocket_count > 0:
            pygame.draw.rect(surf, r_color, (10, 100, 200, 10))
            
        r_text = f"ROCKETS: {self.rocket_count}/3"
        surf.blit(self.font.render(r_text, True, r_color), (10, 115))

    def draw(self, gestures=None):
        self.draw_scene(gestures)