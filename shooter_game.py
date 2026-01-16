import pygame
import sys
import random
import time

pygame.init()

# ================= WINDOW =================
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Fruits")

clock = pygame.time.Clock()
FPS = 60

# ================= COLORS =================
WHITE = (230, 230, 230)
RED = (200, 80, 80)
GREEN = (80, 200, 140)
BLUE = (90, 140, 220)
DARK = (15, 15, 35)

# ================= ASSETS =================
background = pygame.transform.scale(pygame.image.load("galaxy.jpg"), (WIDTH, HEIGHT))
rocket_img = pygame.transform.scale(pygame.image.load("rocket.png"), (60, 80))
enemy_img = pygame.transform.scale(pygame.image.load("ufo.png"), (60, 40))
bullet_img = pygame.transform.scale(pygame.image.load("bullet.png"), (10, 18))

# ================= FONTS =================
font = pygame.font.SysFont("arial", 18)
big_font = pygame.font.SysFont("arial", 48)

# ================= PLAYER STATS =================
player_hp = 100
max_hp = 100

coins = 0
level = 1
kills = 0
kills_required = level * 5

# ================= WEAPON STATS =================
fire_delay = 400
bullet_damage = 1

# ================= STATE =================
game_over = False
shop_open = False
boss_active = False

last_shot = 0
level_start_time = time.time()

# ================= CLASSES =================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = rocket_img
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed, hp):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.speed = speed
        self.hp = hp
        self.reset()

    def reset(self):
        self.rect.x = random.randint(40, WIDTH - 100)
        self.rect.y = random.randint(-300, -40)

    def update(self):
        global player_hp
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.reset()

        if self.rect.colliderect(player.rect):
            player_hp -= 10
            self.reset()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(enemy_img, (120, 80))
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, -100))
        self.hp = 30 + level * 5
        self.speed = 1

    def update(self):
        global player_hp
        if self.rect.top < 60:
            self.rect.y += self.speed
        if self.rect.colliderect(player.rect):
            player_hp -= 20

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 9

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# ================= GROUPS =================
player = Player()
players = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
boss_group = pygame.sprite.Group()

def spawn_enemies():
    enemies.empty()
    for _ in range(5):
        enemies.add(Enemy(speed=1 + level * 0.3, hp=1 + level // 3))

spawn_enemies()

# ================= GAME LOOP =================
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not shop_open:
                now = pygame.time.get_ticks()
                if now - last_shot > fire_delay:
                    bullets.add(Bullet(player.rect.centerx, player.rect.top))
                    last_shot = now

            if event.key == pygame.K_b:
                shop_open = not shop_open

            # SHOP
            if shop_open:
                if event.key == pygame.K_1 and coins >= 5:
                    coins -= 5
                    fire_delay = 300
                if event.key == pygame.K_2 and coins >= 10:
                    coins -= 10
                    bullet_damage = 2
                if event.key == pygame.K_3 and coins >= 20:
                    coins -= 20
                    bullet_damage = 3
                    fire_delay = 250

        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                pygame.quit()
                sys.exit()

    if not game_over and not shop_open:
        players.update()
        enemies.update()
        bullets.update()
        boss_group.update()

        # BULLET → ENEMY
        for enemy in pygame.sprite.groupcollide(enemies, bullets, False, True):
            enemy.hp -= bullet_damage
            if enemy.hp <= 0:
                enemy.reset()
                kills += 1
                coins += 1

        # BULLET → BOSS
        for boss in pygame.sprite.groupcollide(boss_group, bullets, False, True):
            boss.hp -= bullet_damage
            if boss.hp <= 0:
                boss.kill()
                boss_active = False
                coins += 10
                level += 1
                kills = 0
                kills_required = level * 5
                spawn_enemies()

        # LEVEL UP
        if kills >= kills_required and not boss_active:
            if level % 5 == 0:
                boss_active = True
                boss_group.add(Boss())
            else:
                level += 1
                kills = 0
                kills_required = level * 5
                spawn_enemies()

        if player_hp <= 0:
            game_over = True

    # ================= DRAW =================
    screen.blit(background, (0, 0))
    pygame.draw.rect(screen, DARK, (0, 0, WIDTH, 70))

    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Kills: {kills}/{kills_required}", True, WHITE), (10, 35))
    screen.blit(font.render(f"Coins: {coins}", True, WHITE), (160, 10))

    # HP BAR
    pygame.draw.rect(screen, RED, (300, 30, 150, 15))
    pygame.draw.rect(screen, GREEN, (300, 30, int(150 * player_hp / max_hp), 15))
    screen.blit(font.render("HP", True, WHITE), (270, 28))

    players.draw(screen)
    enemies.draw(screen)
    bullets.draw(screen)
    boss_group.draw(screen)

    # SHOP UI
    if shop_open:
        pygame.draw.rect(screen, DARK, (150, 120, 400, 220))
        screen.blit(font.render("GUN SHOP", True, WHITE), (300, 130))
        screen.blit(font.render("1 - Rifle (5 coins)", True, WHITE), (180, 170))
        screen.blit(font.render("2 - Cannon (10 coins)", True, WHITE), (180, 200))
        screen.blit(font.render("3 - Plasma Gun (20 coins)", True, WHITE), (180, 230))
        screen.blit(font.render("Press B to close", True, WHITE), (180, 260))

    if game_over:
        title = big_font.render("GAME OVER", True, RED)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(font.render("Press R to Exit", True, WHITE),
                    (WIDTH // 2 - 70, HEIGHT // 2 + 20))

    pygame.display.update()

pygame.quit()
sys.exit()
