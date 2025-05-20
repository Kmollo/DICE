import pygame
import sys
import random

# Initialize
pygame.init()
pygame.font.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dice Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 225)
VBlue = (50, 74, 178)
RED = (255, 0, 0)

# Font
font = pygame.font.SysFont("Arial", 50)
small_font = pygame.font.SysFont("Arial", 20)
popup_font = pygame.font.SysFont("Arial", 40)

# Load images
try:
    BG = pygame.transform.scale(pygame.image.load("bg.png"), (WIDTH, HEIGHT))
    SPACESHIP_IMAGE = pygame.image.load("spaceship.png")
    SPACESHIP = pygame.transform.scale(SPACESHIP_IMAGE, (40, 60))
    LEVEL2_BG = pygame.transform.scale(pygame.image.load("space1.jpg"), (WIDTH, HEIGHT))
    BOT_IMAGE = pygame.transform.scale(pygame.image.load("bot.png"), (50, 50))
except Exception as e:
    print("Error loading images:", e)
    pygame.quit()
    sys.exit()

# Buttons
button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 80)
continue_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 60)

# Game state
state = "start"
dice_number = None
rolling = False
roll_timer = 0
level_completed = False
transition_to_level2 = False
.0
# Level 1 (beam survival)
PLAYER_VEL = 5
player = pygame.Rect(200, HEIGHT - 110, 40, 60)
beams = []
BEAM_COOLDOWN = 1000
beam_timer = 0
survival_time = 0
start_time = 0

# Level 2 (bots + shooting)
ship_x, ship_y = WIDTH // 2, HEIGHT - 70
bullets = []

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.width = 4
        self.height = 10

    def move(self):
        self.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height))

class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.width = 4
        self.height = 10

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 255), (self.x, self.y, self.width, self.height))

class Bot:
    def __init__(self, x, y):
        self.image = BOT_IMAGE
        self.x = x
        self.y = y
        self.speed = 2
        self.bullets = []
        self.alive = True

    def move(self):
        self.y += self.speed

    def shoot(self):
        bullet = EnemyBullet(self.x + 22, self.y + 50)
        self.bullets.append(bullet)

    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, (self.x, self.y))
        for bullet in self.bullets:
            bullet.move()
            bullet.draw(surface)

bots = [Bot(random.randint(50, WIDTH - 100), random.randint(-300, -50)) for _ in range(3)]

def draw_start():
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, button_rect, width=3, border_radius=20)
    pygame.draw.rect(screen, BLUE, button_rect.inflate(-6, -6), border_radius=20)
    text = font.render("START", True, WHITE)
    screen.blit(text, text.get_rect(center=button_rect.center))

def draw_dice_face(n):
    dot_radius = 10
    die_size = 200
    rect = pygame.Rect(WIDTH // 2 - die_size // 2, HEIGHT // 2 - die_size // 2, die_size, die_size)
    pygame.draw.rect(screen, WHITE, rect, border_radius=20)
    cx, cy = rect.center
    offset = 40
    dot_map = {
        1: [(cx, cy)],
        2: [(cx - offset, cy - offset), (cx + offset, cy + offset)],
        3: [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)],
        4: [(cx - offset, cy - offset), (cx + offset, cy - offset), (cx - offset, cy + offset), (cx + offset, cy + offset)],
        5: [(cx - offset, cy - offset), (cx + offset, cy - offset), (cx, cy), (cx - offset, cy + offset), (cx + offset, cy + offset)],
        6: [(cx - offset, cy - offset), (cx + offset, cy - offset), (cx - offset, cy), (cx + offset, cy), (cx - offset, cy + offset), (cx + offset, cy + offset)]
    }
    for pos in dot_map[n]:
        pygame.draw.circle(screen, BLACK, pos, dot_radius)

def draw_dice():
    screen.fill(BLUE)
    if rolling:
        draw_dice_face(random.randint(1, 6))
    elif dice_number:
        draw_dice_face(dice_number)
        pygame.draw.rect(screen, WHITE, continue_button_rect, border_radius=15)
        text = small_font.render("CONTINUE", True, BLACK)
        screen.blit(text, text.get_rect(center=continue_button_rect.center))
    else:
        draw_dice_face(1)

def draw_level1():
    screen.blit(BG, (0, 0))
    screen.blit(SPACESHIP, (player.x, player.y))
    for beam in beams:
        pygame.draw.rect(screen, RED, beam)
    remaining = max(0, (survival_time - (pygame.time.get_ticks() - start_time)) // 1000)
    timer_text = font.render(str(remaining), True, WHITE)
    screen.blit(timer_text, (WIDTH - 100, 20))
    if level_completed:
        text = popup_font.render("Press any key for Level 2", True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

def draw_level2():
    screen.blit(LEVEL2_BG, (0, 0))
    screen.blit(SPACESHIP, (ship_x, ship_y))
    for bullet in bullets[:]:
        bullet.move()
        bullet.draw(screen)
        if bullet.y < 0:
            bullets.remove(bullet)
    for bot in bots:
        if bot.alive:
            bot.move()
            if random.randint(0, 100) < 2:
                bot.shoot()
            for bullet in bullets[:]:
                if bot.x < bullet.x < bot.x + 50 and bot.y < bullet.y < bot.y + 50:
                    bot.alive = False
                    bullets.remove(bullet)
        else:
            bot.x = random.randint(50, WIDTH - 100)
            bot.y = -60
            bot.alive = True
            bot.bullets.clear()
        if bot.y > HEIGHT:
            bot.x = random.randint(50, WIDTH - 100)
            bot.y = -60
            bot.bullets.clear()
        bot.draw(screen)

clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if state == "start":
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                state = "dice"
        elif state == "dice":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if dice_number and continue_button_rect.collidepoint(event.pos):
                    survival_time = dice_number * 10000
                    start_time = pygame.time.get_ticks()
                    beams.clear()
                    beam_timer = start_time
                    level_completed = False
                    state = "level1"
                else:
                    rolling = True
                    roll_timer = pygame.time.get_ticks()
        elif state == "level1":
            if event.type == pygame.KEYDOWN and level_completed:
                state = "level2"
        elif state == "level2":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullets.append(Bullet(ship_x + 22, ship_y))

    if state == "dice":
        draw_dice()
        if rolling and now - roll_timer > 1000:
            dice_number = random.randint(1, 6)
            rolling = False
    elif state == "level1":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if now - beam_timer > BEAM_COOLDOWN:
            beams.append(pygame.Rect(random.randint(0, WIDTH - 10), 0, 10, 30))
            beam_timer = now
        for beam in beams[:]:
            beam.y += 5
            if beam.colliderect(player):
                beams.remove(beam)
        if not level_completed and now - start_time >= survival_time:
            level_completed = True
        draw_level1()
    elif state == "level2":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and ship_x > 0:
            ship_x -= 5
        if keys[pygame.K_RIGHT] and ship_x < WIDTH - 50:
            ship_x += 5
        if keys[pygame.K_UP] and ship_y > 0:
            ship_y -= 5
        if keys[pygame.K_DOWN] and ship_y < HEIGHT - 50:
            ship_y += 5
        draw_level2()
    elif state == "start":
        draw_start()

    pygame.display.flip()
    clock.tick(60)