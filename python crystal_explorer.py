import pygame
import random
import sys
import os
import json
from math import sin, cos, radians
import math  # <-- DITAMBAHKAN: untuk laser

# Inisialisasi
pygame.init()
pygame.mixer.init()

# Konstanta
WIDTH, HEIGHT = 480, 640
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
BLUE = (30, 144, 255)
GREEN = (50, 205, 50) 
ORANGE = (255, 140, 0)
GRAY = (169, 169, 169)
DARK_BLUE = (0, 70, 130)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
DARK_GRAY = (64, 64, 64)
SILVER = (192, 192, 192)
STEALTH_BLACK = (30, 30, 40)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JET STRIKER: STEALTH BOMBER STRIKE")
clock = pygame.time.Clock()

# Font
font_small = pygame.font.SysFont("consolas", 18)
font_medium = pygame.font.SysFont("consolas", 26, bold=True)
font_large = pygame.font.SysFont("consolas", 48, bold=True)

# High score
SCORE_FILE = "highscore.json"
high_score = 0
if os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "r") as f:
        data = json.load(f)
        high_score = data.get("high_score", 0)

# === DESAIN PESAWAT TEMPUR VARIASI ===
def draw_jet_fighter(surface, color, burn=False, size=(60, 70), variant=0):
    w, h = size
    surface.fill((0, 0, 0, 0))

    body_points = [(w//2, 0), (w//2 - 8, 20), (w//2 - 12, h-10), (w//2, h), (w//2 + 12, h-10), (w//2 + 8, 20)]
    pygame.draw.polygon(surface, color, body_points)
    pygame.draw.polygon(surface, LIGHT_BLUE, body_points, 2)

    if variant == 0:
        left_wing = [(w//2 - 20, 25), (0, 35), (10, 40), (w//2 - 12, 35)]
    elif variant == 1:
        left_wing = [(w//2 - 25, 20), (5, 40), (15, 45), (w//2 - 10, 30)]
    else:
        left_wing = [(w//2 - 18, 30), (0, 38), (8, 42), (w//2 - 15, 35)]
    right_wing = [(w - p[0], p[1]) for p in left_wing[::-1]]
    pygame.draw.polygon(surface, color, left_wing)
    pygame.draw.polygon(surface, color, right_wing)
    pygame.draw.polygon(surface, WHITE, left_wing, 1)
    pygame.draw.polygon(surface, WHITE, right_wing, 1)

    pygame.draw.polygon(surface, color, [(w//2 - 5, 5), (w//2 - 3, 15), (w//2, 18), (w//2 + 3, 15), (w//2 + 5, 5)])
    if variant % 2 == 0:
        pygame.draw.line(surface, WHITE, (w//2 - 2, 8), (w//2 + 2, 8), 2)

    pygame.draw.ellipse(surface, (200, 220, 255), (w//2 - 6, 12, 12, 14))
    pygame.draw.ellipse(surface, WHITE, (w//2 - 5, 13, 10, 10), 1)

    flame_color = YELLOW if not burn else ORANGE
    pygame.draw.ellipse(surface, flame_color, (w//2 - 10, h-15, 20, 12))
    pygame.draw.ellipse(surface, ORANGE, (w//2 - 6, h-18, 12, 10))
    pygame.draw.circle(surface, WHITE, (w//2, h-12), 2)

    if burn:   
        pygame.draw.circle(surface, ORANGE, (w//2 - 15, 40), 8)
        pygame.draw.circle(surface, YELLOW, (w//2 + 15, 38), 6)
        pygame.draw.circle(surface, RED, (w//2, 30), 5)

def draw_enemy_jet(surface, size=(55, 65), variant=0):
    w, h = size
    surface.fill((0, 0, 0, 0))

    if variant == 0:
        body_points = [(w//2, 0), (w//2 - 10, 25), (w//2 - 15, h-10), (w//2, h), (w//2 + 15, h-10), (w//2 + 10, 25)]
    elif variant == 1:
        body_points = [(w//2, 5), (w//2 - 12, 30), (w//2 - 18, h-5), (w//2, h), (w//2 + 18, h-5), (w//2 + 12, 30)]
    else:
        body_points = [(w//2, 0), (w//2 - 8, 28), (w//2 - 13, h-8), (w//2, h), (w//2 + 13, h-8), (w//2 + 8, 28)]
    pygame.draw.polygon(surface, RED, body_points)
    pygame.draw.polygon(surface, (255, 100, 100), body_points, 2)

    if variant == 0:
        left_wing = [(5, 30), (0, 40), (15, 38), (20, 30)]
    elif variant == 1:
        left_wing = [(10, 25), (2, 45), (18, 42), (25, 28)]
    else:
        left_wing = [(8, 32), (0, 42), (12, 40), (22, 32)]
    right_wing = [(w - p[0], p[1]) for p in left_wing[::-1]]
    pygame.draw.polygon(surface, RED, left_wing)
    pygame.draw.polygon(surface, RED, right_wing)

    pygame.draw.polygon(surface, DARK_GRAY, [(w//2 - 8, 10), (w//2 - 5, 20), (w//2 - 10, 22)])
    pygame.draw.polygon(surface, DARK_GRAY, [(w//2 + 8, 10), (w//2 + 5, 20), (w//2 + 10, 22)])

    pygame.draw.ellipse(surface, (139, 0, 0), (w//2 - 5, 15, 10, 12))
    pygame.draw.ellipse(surface, ORANGE, (w//2 - 8, h-12, 16, 10))
    pygame.draw.circle(surface, RED, (w//2, h-8), 3)

def draw_boss_carrier(surface, size=(140, 120), glow_phase=0, variant=0):
    w, h = size
    surface.fill((0, 0, 0, 0))

    glow_alpha = int(40 + 25 * sin(glow_phase * 0.15))
    glow_surf = pygame.Surface((w+30, h+30), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (255, 50, 50, glow_alpha), (15, 35, w, h-40), border_radius=15)
    surface.blit(glow_surf, (-15, -15))

    if variant == 0:
        pygame.draw.rect(surface, SILVER, (0, 20, w, h-30))
        pygame.draw.rect(surface, DARK_GRAY, (5, 25, w-10, h-35))
        pygame.draw.rect(surface, DARK_BLUE, (15, 35, w-30, h-50))
    else:
        pygame.draw.rect(surface, GRAY, (0, 15, w, h-25))
        pygame.draw.rect(surface, SILVER, (5, 20, w-10, h-30))
        pygame.draw.rect(surface, DARK_GRAY, (15, 30, w-30, h-45))

    pygame.draw.rect(surface, GRAY, (w//2 - 25, 5, 50, 30))
    pygame.draw.rect(surface, RED, (w//2 - 20, 10, 40, 20))
    pygame.draw.rect(surface, DARK_GRAY, (w//2 - 22, 12, 44, 16))

    left_gun = pygame.Rect(20, 35, 25, 15) if variant == 0 else pygame.Rect(15, 30, 30, 20)
    pygame.draw.rect(surface, RED, left_gun)
    pygame.draw.rect(surface, DARK_GRAY, left_gun.inflate(-4, -4))
    pygame.draw.rect(surface, ORANGE, left_gun.move(2, 2).inflate(-4, -4))

    right_gun = pygame.Rect(w-45, 35, 25, 15) if variant == 0 else pygame.Rect(w-45, 30, 30, 20)
    pygame.draw.rect(surface, RED, right_gun)
    pygame.draw.rect(surface, DARK_GRAY, right_gun.inflate(-4, -4))
    pygame.draw.rect(surface, ORANGE, right_gun.move(2, 2).inflate(-4, -4))

    antenna_glow = int(255 * (0.7 + 0.3 * sin(glow_phase * 0.12)))
    pygame.draw.line(surface, (GOLD[0], GOLD[1], antenna_glow), (w//2, 0), (w//2, 15), 5)
    pygame.draw.circle(surface, GOLD, (w//2, 15), 6)

    for i in range(20, w-20, 25):
        pygame.draw.line(surface, WHITE, (i, 40), (i, h-20), 1)
    pygame.draw.line(surface, YELLOW    , (w//2 - 15, 25), (w//2 + 15, 25), 2)

# === B-2 SPIRIT STEALTH BOMBER DARI BELAKANG (VIEW DARI BELAKANG) ===
def draw_stealth_bomber(surface, size=(WIDTH+120, 280)):
    w, h = size
    surface.fill((0, 0, 0, 0))

    # Badan utama B-2 (bentuk wajik)
    body_points = [
        (w//2, 40),  # Hidung
        (w//2 - 120, 100),
        (w//2 - 160, 180),
        (w//2 - 100, h-40),
        (w//2 + 100, h-40),
        (w//2 + 160, 180),
        (w//2 + 120, 100)
    ]
    pygame.draw.polygon(surface, STEALTH_BLACK, body_points)
    pygame.draw.polygon(surface, (50, 50, 60), body_points, 3)

    # Sayap belakang (zigzag stealth)
    wing_left = [(w//2 - 100, h-40), (w//2 - 200, h-20), (w//2 - 160, h-60), (w//2 - 80, h-60)]
    wing_right = [(w//2 + 100, h-40), (w//2 + 200, h-20), (w//2 + 160, h-60), (w//2 + 80, h-60)]
    pygame.draw.polygon(surface, STEALTH_BLACK, wing_left)
    pygame.draw.polygon(surface, STEALTH_BLACK, wing_right)
    pygame.draw.polygon(surface, (60, 60, 70), wing_left, 2)
    pygame.draw.polygon(surface, (60, 60, 70), wing_right, 2)

    # Mesin ganda (exhaust)
    for x in [w//2 - 90, w//2 - 30, w//2 + 30, w//2 + 90]:
        pygame.draw.ellipse(surface, (100, 100, 150), (x-25, h-100, 50, 40))
        pygame.draw.ellipse(surface, (150, 150, 200), (x-20, h-95, 40, 30))
        pygame.draw.circle(surface, (200, 200, 255), (x, h-75), 10)

    # Garis panel stealth
    for i in range(w//2 - 140, w//2 + 140, 40):
        pygame.draw.line(surface, (70, 70, 80), (i, 120), (i+20, 140), 1)
        pygame.draw.line(surface, (70, 70, 80), (i, 140), (i+20, 120), 1)

    # Logo USAF kecil
    pygame.draw.circle(surface, WHITE, (w//2, 80), 12)
    pygame.draw.circle(surface, RED, (w//2, 80), 12, 2)
    pygame.draw.circle(surface, BLUE, (w//2, 80), 8)
    pygame.draw.polygon(surface, WHITE, [(w//2-4,76), (w//2,84), (w//2+4,76)])

# === FUNGSI HEAL POWERUP YANG HILANG ===
def draw_heal_powerup(surface, size=(40, 40)):
    w, h = size
    surface.fill((0, 0, 0, 0))
    heart_points = [(20,8),(30,3),(40,8),(35,18),(25,30),(15,18)]
    pygame.draw.polygon(surface, RED, heart_points)
    pygame.draw.polygon(surface, (255, 192, 203), heart_points, 3)
    pygame.draw.circle(surface, WHITE, (w//2, h//2), 14)
    pygame.draw.line(surface, RED, (w//2-6, h//2), (w//2+6, h//2), 4)
    pygame.draw.line(surface, RED, (w//2, h//2-6), (w//2, h//2+6), 4)

# === TAMBAHAN: GAMBAR BACKGROUND AWAN DINAMIS (SENDIRI, TIDAK DARI FILE) ===
def draw_cloud(surface, x, y, scale=1.0, alpha=50):
    s = int(60 * scale)
    surf = pygame.Surface((s*3, s*2), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (200, 220, 255, alpha), (0, s//2, s, s))
    pygame.draw.ellipse(surf, (200, 220, 255, alpha), (s//2, s//3, s, s))
    pygame.draw.ellipse(surf, (200, 220, 255, alpha), (s, s//2, s, s))
    pygame.draw.ellipse(surf, (200, 220, 255, alpha), (s//3, s//4, s, s))
    surface.blit(surf, (x - s*1.5, y - s))

# Buat sprite
def create_surface(size):
    return pygame.Surface(size, pygame.SRCALPHA)

player_img = create_surface((60, 70))
draw_jet_fighter(player_img, BLUE, variant=0)

player_burn_img = create_surface((60, 70))
draw_jet_fighter(player_burn_img, RED, burn=True, variant=0)

enemy_imgs = []
for v in range(3):
    img = create_surface((55, 65))
    draw_enemy_jet(img, variant=v)
    enemy_imgs.append(img)

boss_imgs = []
for v in range(2):
    img = create_surface((140, 120))
    draw_boss_carrier(img, variant=v)
    boss_imgs.append(img)

# B-2 Spirit dari belakang
b2_bomber_img = create_surface((WIDTH+120, 280))
draw_stealth_bomber(b2_bomber_img)

bullet_img = pygame.Surface((8, 24), pygame.SRCALPHA)
pygame.draw.rect(bullet_img, YELLOW, (0, 0, 8, 24))
pygame.draw.circle(bullet_img, WHITE, (4, 0), 4)
pygame.draw.rect(bullet_img, ORANGE, (1, 4, 6, 18))

powerup_imgs = {ptype: create_surface((40, 40)) for ptype in ["double", "shield", "bomb", "heal"]}

pygame.draw.circle(powerup_imgs["double"], GREEN, (20,20), 18)
pygame.draw.line(powerup_imgs["double"], YELLOW, (10,20), (30,20), 5)
pygame.draw.line(powerup_imgs["double"], YELLOW, (20,10), (20,30), 5)

pygame.draw.circle(powerup_imgs["shield"], BLUE, (20,20), 18)
pygame.draw.circle(powerup_imgs["shield"], WHITE, (20,20), 18, 4)
pygame.draw.circle(powerup_imgs["shield"], LIGHT_BLUE, (20,20), 14, 2)

pygame.draw.circle(powerup_imgs["bomb"], RED, (20,20), 16)
pygame.draw.line(powerup_imgs["bomb"], BLACK, (15,10), (25,10), 4)

# PANGGIL FUNGSI HEAL YANG HILANG
draw_heal_powerup(powerup_imgs["heal"])

# Partikel
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype="explosion"):
        super().__init__()
        if ptype == "smoke":
            self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (100, 100, 100, 200), (6, 6), 6)
            self.vel_x = random.uniform(-2, 2)
            self.vel_y = random.uniform(-1.5, 0.5)
        else:
            size = random.randint(12, 40)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            color = random.choice([ORANGE, YELLOW, RED])
            pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
            pygame.draw.circle(self.image, WHITE, (size//2, size//2), size//4)
            self.vel_x = random.uniform(-8, 8)
            self.vel_y = random.uniform(-12, -5)
        self.rect = self.image.get_rect(center=(x, y))
        self.life = random.randint(25, 45)
        self.max_life = self.life

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 0.4
        self.life -= 1
        alpha = int(255 * (self.life / self.max_life))
        self.image.set_alpha(alpha)
        if self.life <= 0:
            self.kill()

# Kelas Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 40
        self.speed = 7.5
        self.lives = 3
        self.max_lives = 5
        self.score = 0
        self.shoot_delay = 160
        self.last_shot = 0
        self.power = 1
        self.shield = 0
        self.bombs = 3
        self.burning = 0
        self.smoke_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())

        if self.burning > 0:
            self.burning -= clock.get_time()
            self.smoke_timer -= 1
            if self.smoke_timer <= 0:
                smoke = Particle(self.rect.centerx + random.randint(-20,20), self.rect.bottom, "smoke")
                all_sprites.add(smoke); particles.add(smoke)
                self.smoke_timer = random.randint(4, 8)
            self.image = player_burn_img if int(pygame.time.get_ticks() / 70) % 2 else player_img
        else:
            self.image = player_img

    def hit(self):
        self.burning = 1300
        self.smoke_timer = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                b = Bullet(self.rect.centerx, self.rect.top + 10)
                all_sprites.add(b); bullets.add(b)
            else:
                b1 = Bullet(self.rect.left + 20, self.rect.top + 15)
                b2 = Bullet(self.rect.right - 20, self.rect.top + 15)
                all_sprites.add(b1, b2); bullets.add(b1, b2)

    def bomb(self):
        if self.bombs > 0 and not any(isinstance(s, B2Bomber) for s in all_sprites):
            self.bombs -= 1
            bomber = B2Bomber()
            all_sprites.add(bomber)
            b2_bombers.add(bomber)

    def heal(self):
        if self.lives < self.max_lives:
            self.lives += 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.speed = -18
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0: self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, type=0):
        super().__init__()
        self.image = enemy_imgs[type % len(enemy_imgs)]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-120, -50)
        self.speed = random.randint(3, 6)
        self.health = 1
        self.shoot_timer = random.randint(80, 200)
    def update(self):
        self.rect.y += self.speed
        self.shoot_timer -= 1
        if self.shoot_timer <= 0 and self.rect.top > 0:
            b = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(b); enemy_bullets.add(b)
            self.shoot_timer = random.randint(100, 250)
        if self.rect.top > HEIGHT: self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0,0,6,18))
        pygame.draw.circle(self.image, ORANGE, (3,0), 3)
        self.rect = self.image.get_rect(centerx=x, top=y)
        self.speed = 6
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_image = random.choice(boss_imgs)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(centerx=WIDTH//2, top=-100)
        self.speed = 1.2
        self.health = 10
        self.shoot_timer = 0
        self.glow_phase = 0

    def update(self):
        self.glow_phase += 1
        self.image = self.base_image.copy()
        draw_boss_carrier(self.image, glow_phase=self.glow_phase)

        if self.rect.top < 80:
            self.rect.y += self.speed
        else:
            self.shoot_timer += 1
            if self.shoot_timer >= 90:
                self.shoot_timer = 0
                b1 = EnemyBullet(self.rect.left + 30, self.rect.top + 50)
                b2 = EnemyBullet(self.rect.right - 30, self.rect.top + 50)
                all_sprites.add(b1, b2)
                enemy_bullets.add(b1, b2)

        if self.health <= 0:
            explode(self.rect.centerx, self.rect.centery, big=True)
            self.kill()
            player.score += 150

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, ptype, x, y):
        super().__init__()
        self.type = ptype
        self.image = powerup_imgs[ptype]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2.5
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()

# B-2 SPIRIT BOMBER: Muncul dari atas, diam, hancurkan semua
class B2Bomber(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = b2_bomber_img
        self.rect = self.image.get_rect(centerx=WIDTH//2, top=-280)
        self.state = "entering"  # entering -> pause -> attack -> leaving
        self.timer = 0
        self.pause_time = 90  # 1.5 detik
        self.attack_time = 150  # 2.5 detik
        self.speed = 4

    def update(self):
        self.timer += 1

        if self.state == "entering":
            self.rect.y += self.speed
            if self.rect.top >= 60:
                self.state = "pause"
                self.timer = 0

        elif self.state == "pause":
            if self.timer >= self.pause_time:
                self.state = "attack"
                self.timer = 0

        elif self.state == "attack":
            if self.timer % 6 == 0:  # Setiap 0.1 detik
                for enemy in list(enemies):
                    # Laser dari bomber ke musuh
                    laser = StealthLaser(self.rect.centerx, self.rect.bottom - 40, enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(laser)
                    lasers.add(laser)
                    # Hancurkan
                    explode(enemy.rect.centerx, enemy.rect.centery)
                    enemy.kill()
                    player.score += 10
            if self.timer >= self.attack_time:
                self.state = "leaving"
                self.timer = 0

        elif self.state == "leaving":
            self.rect.y -= self.speed * 1.8
            if self.rect.bottom < 0:
                self.kill()

# Laser stealth (biru dingin)
class StealthLaser(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        dx = x2 - x1
        dy = y2 - y1
        dist = max(abs(dx), abs(dy), 10)
        self.image = pygame.Surface((int(abs(dx))+20, int(abs(dy))+20), pygame.SRCALPHA)
        color = (100, 150, 255, 200)
        pygame.draw.line(self.image, color, (10 if dx >= 0 else abs(dx)+10, 10 if dy >= 0 else abs(dy)+10),
                        (10 + dx if dx >= 0 else 10, 10 + dy if dy >= 0 else 10), 5)
        pygame.draw.line(self.image, (150, 200, 255), (10 if dx >= 0 else abs(dx)+10, 10 if dy >= 0 else abs(dy)+10),
                        (10 + dx if dx >= 0 else 10, 10 + dy if dy >= 0 else 10), 2)
        self.rect = self.image.get_rect(center=(x1 + dx//2, y1 + dy//2))
        self.life = 12

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()

def explode(x, y, big=False):
    num = 25 if not big else 50
    for _ in range(num):
        p = Particle(x, y)
        all_sprites.add(p); particles.add(p)

# Grup
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
particles = pygame.sprite.Group()
b2_bombers = pygame.sprite.Group()
lasers = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Variabel
running = True
game_state = "menu"
level = 1
boss = None
spawn_timer = 0
enemies_killed = 0

# Tombol
class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=12)
        txt = font_medium.render(self.text, True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.rect.center))
    def check_click(self, pos):
        if self.rect.collidepoint(pos): self.action()

start_btn = Button(WIDTH//2 - 100, 300, 200, 50, "START", lambda: start_game())
restart_btn = Button(WIDTH//2 - 100, 350, 200, 50, "RESTART", lambda: start_game())

def start_game():
    global game_state, level, boss, spawn_timer, enemies_killed
    game_state = "playing"
    level = 1; boss = None; spawn_timer = 0; enemies_killed = 0
    player.lives = 3; player.power = 1; player.shield = 0; player.bombs = 3; player.burning = 0
    for s in all_sprites: s.kill()
    all_sprites.add(player)
    [g.empty() for g in [enemies, bullets, enemy_bullets, powerups, particles, b2_bombers, lasers]]

def save_highscore():
    global high_score
    if player.score > high_score:
        high_score = player.score
        with open(SCORE_FILE, "w") as f:
            json.dump({"high_score": high_score}, f)

# === TAMBAHAN: EFEK GETAR & SLOW MOTION ===
shake_time = shake_intensity = 0
def screen_shake(duration=30, intensity=8):
    global shake_time, shake_intensity
    shake_time, shake_intensity = duration, intensity

slow_motion_time = slow_motion_factor = 1.0
def set_slow_motion(factor=0.3, duration=120):
    global slow_motion_time, slow_motion_factor
    slow_motion_time, slow_motion_factor = duration, factor

# === SUARA (dengan fallback) ===
try:
    shoot_sound = pygame.mixer.Sound(buffer=b'\x52\x49\x46\x46\x24\x08\x00\x00\x57\x41\x56\x45\x66\x6d\x74\x20\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00\x64\x61\x74\x61\x00\x08\x00\x00')
    shoot_sound.set_volume(0.3)
    explode_sound = pygame.mixer.Sound(buffer=b'\x52\x49\x46\x46\x24\x08\x00\x00\x57\x41\x56\x45\x66\x6d\x74\x20\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00\x64\x61\x74\x61\x00\x08\x00\x00')
    explode_sound.set_volume(0.5)
    bomb_sound = pygame.mixer.Sound(buffer=b'\x52\x49\x46\x46\x24\x08\x00\x00\x57\x41\x56\x45\x66\x6d\x74\x20\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00\x64\x61\x74\x61\x00\x08\x00\x00')
    bomb_sound.set_volume(0.8)
    powerup_sound = pygame.mixer.Sound(buffer=b'\x52\x49\x46\x46\x24\x08\x00\x00\x57\x41\x56\x45\x66\x6d\x74\x20\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00\x64\x61\x74\x61\x00\x08\x00\x00')
    powerup_sound.set_volume(0.6)
except:
    shoot_sound = explode_sound = bomb_sound = powerup_sound = None

# === PERBAIKI B-2: TAMBAHKAN EFEK ===
def update_b2_with_effects():
    if any(isinstance(s, B2Bomber) for s in all_sprites):
        for b2 in b2_bombers:
            if b2.state == "pause" and b2.timer == 1:
                screen_shake(40, 12)
                set_slow_motion(0.3, 120)
                if bomb_sound: bomb_sound.play()

# === TAMBAHAN: CLOUDS DINAMIS (GAMBAR SENDIRI) ===
clouds = []
for _ in range(8):
    clouds.append({
        'x': random.randint(-200, WIDTH + 200),
        'y': random.randint(0, HEIGHT),
        'scale': random.uniform(0.6, 1.4),
        'speed': random.uniform(0.2, 0.6)
    })

# Main Loop
background_y = 0
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(120)]

while running:
    dt = clock.tick(FPS) * slow_motion_factor
    if slow_motion_time > 0: slow_motion_time -= 1
    else: slow_motion_factor = 1.0

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN: mouse_clicked = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "playing":
                player.shoot()
                if shoot_sound: shoot_sound.play()
            if event.key == pygame.K_b and game_state == "playing":
                player.bomb()
                if bomb_sound: bomb_sound.play()
            if event.key == pygame.K_p: game_state = "paused" if game_state == "playing" else "playing"

    # Background
    screen.fill((10, 10, 30))
    shake_offset = (0, 0)
    if shake_time > 0:
        shake_offset = (random.randint(-shake_intensity, shake_intensity), random.randint(-shake_intensity, shake_intensity))
        shake_time -= 1
    for x, y in stars:
        py = (y + background_y) % HEIGHT
        pygame.draw.circle(screen, WHITE, (x + shake_offset[0], int(py) + shake_offset[1]), 1)
    background_y = (background_y + 1.2 * slow_motion_factor) % HEIGHT

    # === GAMBAR AWAN DINAMIS (SENDIRI) ===
    for cloud in clouds:
        cloud['x'] -= cloud['speed'] * slow_motion_factor
        if cloud['x'] < -300: cloud['x'] = WIDTH + 200
        draw_cloud(screen, cloud['x'] + shake_offset[0], cloud['y'] + shake_offset[1], cloud['scale'], alpha=40)

    if game_state == "menu":
        txt = font_large.render("JET STRIKER", True, YELLOW)
        screen.blit(txt, txt.get_rect(center=(WIDTH//2 + shake_offset[0], 160 + shake_offset[1])))
        txt = font_small.render("WASD/ARROW = MOVE | SPACE = FIRE | B = B-2 STRIKE | P = PAUSE", True, WHITE)
        screen.blit(txt, txt.get_rect(center=(WIDTH//2 + shake_offset[0], 230 + shake_offset[1])))
        start_btn.draw()
        if mouse_clicked: start_btn.check_click(mouse_pos)

    elif game_state in ["playing", "paused"]:
        if game_state == "playing":
            spawn_timer += dt
            spawn_rate = max(400, 1400 - player.score * 1.8)
            if spawn_timer > spawn_rate:
                e = Enemy(random.randint(0, 2))
                all_sprites.add(e); enemies.add(e)
                spawn_timer = 0

            if player.score > 0 and player.score % 600 < 12 and not boss:
                boss = Boss()
                all_sprites.add(boss); enemies.add(boss)

            all_sprites.update()
            update_b2_with_effects()  # <-- TAMBAHAN EFEK B-2

            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for e, _ in hits.items():
                e.health -= 1
                if e.health <= 0:
                    if explode_sound: explode_sound.play()
                    explode(e.rect.centerx, e.rect.centery)
                    e.kill()
                    player.score += 10
                    enemies_killed += 1
                    if random.random() < 0.15 + min(enemies_killed, 40)/400:
                        pu = PowerUp("heal", e.rect.centerx, e.rect.centery)
                        all_sprites.add(pu); powerups.add(pu)
                    elif random.random() < 0.18:
                        pu = PowerUp(random.choice(["double", "shield", "bomb"]), e.rect.centerx, e.rect.centery)
                        all_sprites.add(pu); powerups.add(pu)

            for pu in pygame.sprite.spritecollide(player, powerups, True):
                if powerup_sound: powerup_sound.play()
                if pu.type == "double": player.power = 2
                elif pu.type == "shield": player.shield = 3500
                elif pu.type == "bomb": player.bombs += 1
                elif pu.type == "heal": player.heal()

            if player.shield <= 0:
                hits = pygame.sprite.spritecollide(player, enemies, True) or pygame.sprite.spritecollide(player, enemy_bullets, True)
                if hits:
                    player.hit()
                    player.lives -= 1
                    explode(player.rect.centerx, player.rect.centery)
                    if player.lives <= 0:
                        save_highscore()
                        game_state = "gameover"
            else:
                for e in pygame.sprite.spritecollide(player, enemies, True):
                    explode(e.rect.centerx, e.rect.centery)
                    player.score += 10
                pygame.sprite.spritecollide(player, enemy_bullets, True)

            if player.shield > 0: player.shield -= dt
            new_level = player.score // 250 + 1
            if new_level > level: level = new_level

        all_sprites.draw(screen)
        lasers.draw(screen)

        if player.shield > 0:
            alpha = int(160 + 90 * sin(pygame.time.get_ticks() * 0.012))
            s = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 200, 255, alpha), (50, 50), 45, 7)
            screen.blit(s, s.get_rect(center=player.rect.center))

        y = 12
        screen.blit(font_medium.render(f"SCORE: {player.score}", True, WHITE), (12, y))
        screen.blit(font_medium.render(f"LVL: {level}", True, YELLOW), (12, y+28))
        screen.blit(font_medium.render(f"LIVES: {player.lives}/{player.max_lives}", True, RED), (WIDTH-170, y))
        screen.blit(font_medium.render(f"B-2: {player.bombs}", True, GREEN), (WIDTH-140, y+28))

        if player.shield > 0:
            fill = (player.shield / 3500) * 110
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 55, y, 110, 12), 2)
            pygame.draw.rect(screen, BLUE, (WIDTH//2 - 55, y, fill, 12))

        if game_state == "paused":
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(160); overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            screen.blit(font_large.render("PAUSED", True, YELLOW), (WIDTH//2 - 100, HEIGHT//2))

    elif game_state == "gameover":
        overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(210); overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        screen.blit(font_large.render("GAME OVER", True, RED), (WIDTH//2 - 140, HEIGHT//2 - 60))
        screen.blit(font_medium.render(f"SCORE: {player.score} | HIGH: {high_score}", True, WHITE), (WIDTH//2 - 160, HEIGHT//2))
        restart_btn.draw()
        if mouse_clicked: restart_btn.check_click(mouse_pos)

    pygame.display.flip()

pygame.quit()
sys.exit()