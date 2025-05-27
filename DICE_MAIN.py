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
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Font
font = pygame.font.SysFont("Arial", 50)
small_font = pygame.font.SysFont("Arial", 20)
popup_font = pygame.font.SysFont("Arial", 40)
medium_font = pygame.font.SysFont("Arial", 30)

# Load images
try:
    BG = pygame.transform.scale(pygame.image.load("assets/bg.png"), (WIDTH, HEIGHT))
    SPACESHIP_IMAGE = pygame.image.load("assets/spaceship.png")
    SPACESHIP = pygame.transform.scale(SPACESHIP_IMAGE, (40, 60))
    LEVEL2_BG = pygame.transform.scale(pygame.image.load("assets/space1.jpg"), (WIDTH, HEIGHT))
    BOT_IMAGE = pygame.transform.scale(pygame.image.load("assets/bot.png"), (50, 50))
    # Level 3 assets
    LEVEL3_BG = pygame.transform.scale(pygame.image.load("assets/2BG.jpg"), (WIDTH, HEIGHT))
    RED_SPACESHIP_IMAGE = pygame.image.load("assets/Red_space_ship.png")
    RED_SPACESHIP = pygame.transform.scale(RED_SPACESHIP_IMAGE, (40, 60))
except Exception as e:
    print("Error loading images:", e)
    pygame.quit()
    sys.exit()

# Buttons
button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 80)
continue_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 60)
level3_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50)

# Level selection butto
level1_button_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 40, 180, 80)
level2_button_rect = pygame.Rect(WIDTH // 2 - 90, HEIGHT // 2 - 40, 180, 80)
level3_select_button_rect = pygame.Rect(WIDTH // 2 + 120, HEIGHT // 2 - 40, 180, 80)

# Game state
state = "start"
dice_number = None
rolling = False
roll_timer = 0
level_completed = False
transition_to_level2 = False
level2_won = False

# Level 3 progression system
level3_dice_rolled = False
level3_dice_number = None
level3_score_requirement = 0
level3_dice_rolling = False
level3_dice_roll_timer = 0
level3_unlocked = False
current_score = 0

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
bots = []
life_count = 0
bots_killed = 0

# Level 3 (enhanced combat)
level3_ship_x, level3_ship_y = WIDTH // 2, HEIGHT - 70
level3_bullets = []
level3_life_count = 0
level3_bots_killed = 0
level3_bots = []

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

class Level3EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 6
        self.width = 6
        self.height = 15

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))

class Level3Bot:
    def __init__(self, x, y):
        self.image = BOT_IMAGE
        self.x = x
        self.y = y
        self.speed = 3
        self.bullets = []
        self.alive = True

    def move(self):
        self.y += self.speed

    def shoot(self):
        bullet = Level3EnemyBullet(self.x + 22, self.y + 50)
        self.bullets.append(bullet)

    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, (self.x, self.y))
        for bullet in self.bullets:
            bullet.move()
            bullet.draw(surface)

def initialize_level1():
    """Initialize Level 1 game state"""
    global player, beams, beam_timer, survival_time, start_time, level_completed
    player = pygame.Rect(200, HEIGHT - 110, 40, 60)
    beams = []
    survival_time = dice_number * 10000
    start_time = pygame.time.get_ticks()
    beam_timer = start_time
    level_completed = False

def initialize_level2():
    """Initialize Level 2 game state"""
    global ship_x, ship_y, bullets, life_count, bots_killed, bots, current_score
    ship_x, ship_y = WIDTH // 2, HEIGHT - 70
    bullets = []
    life_count = dice_number
    bots_killed = 0
    current_score = 0
    bots = [Bot(random.randint(50, WIDTH - 100), random.randint(-300, -50)) for _ in range(3)]

def initialize_level3():
    """Initialize Level 3 game state"""
    global level3_ship_x, level3_ship_y, level3_bullets, level3_life_count, level3_bots_killed, level3_bots
    level3_ship_x, level3_ship_y = WIDTH // 2, HEIGHT - 70
    level3_bullets = []
    level3_life_count = dice_number
    level3_bots_killed = 0
    level3_bots = [Level3Bot(random.randint(50, WIDTH - 100), random.randint(-300, -50)) for _ in range(4)]

def draw_level_selection():
    """Draw the level selection screen"""
    screen.fill(VBlue)
    
    # Title
    title_text = popup_font.render("SELECT LEVEL", True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150)))
    
    # Dice result display
    dice_text = medium_font.render(f"Dice Roll: {dice_number}", True, YELLOW)
    screen.blit(dice_text, dice_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
    
    # Level 1 Button
    pygame.draw.rect(screen, GREEN, level1_button_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, level1_button_rect, width=3, border_radius=10)
    level1_text = medium_font.render("LEVEL 1", True, BLACK)
    screen.blit(level1_text, level1_text.get_rect(center=level1_button_rect.center))
    level1_desc = small_font.render("Beam Survival", True, WHITE)
    screen.blit(level1_desc, level1_desc.get_rect(center=(level1_button_rect.centerx, level1_button_rect.bottom + 15)))
    
    # Level 2 Button
    pygame.draw.rect(screen, BLUE, level2_button_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, level2_button_rect, width=3, border_radius=10)
    level2_text = medium_font.render("LEVEL 2", True, WHITE)
    screen.blit(level2_text, level2_text.get_rect(center=level2_button_rect.center))
    level2_desc = small_font.render("Space Combat", True, WHITE)
    screen.blit(level2_desc, level2_desc.get_rect(center=(level2_button_rect.centerx, level2_button_rect.bottom + 15)))
    
    # Level 3 Button
    pygame.draw.rect(screen, PURPLE, level3_select_button_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, level3_select_button_rect, width=3, border_radius=10)
    level3_text = medium_font.render("LEVEL 3", True, WHITE)
    screen.blit(level3_text, level3_text.get_rect(center=level3_select_button_rect.center))
    level3_desc = small_font.render("Enhanced Combat", True, WHITE)
    screen.blit(level3_desc, level3_desc.get_rect(center=(level3_select_button_rect.centerx, level3_select_button_rect.bottom + 15)))
    
    # Instructions
    instruction_text = small_font.render("Click on a level to begin", True, WHITE)
    screen.blit(instruction_text, instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))

def draw_level3():
    """Draw Level 3 gameplay"""
    global level3_life_count, level3_bots_killed
    
    if level3_life_count <= 0:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 100)))
        return
    
    screen.blit(LEVEL3_BG, (0, 0))
    screen.blit(RED_SPACESHIP, (level3_ship_x, level3_ship_y))
    
    for bullet in level3_bullets[:]:
        bullet.move()
        bullet.draw(screen)
        if bullet.y < 0:
            level3_bullets.remove(bullet)
    
    for bot in level3_bots:
        if bot.alive:
            bot.move()
            if random.randint(0, 100) < 3:
                bot.shoot()
            
            for bullet in level3_bullets[:]:
                if bot.x < bullet.x < bot.x + 50 and bot.y < bullet.y < bot.y + 50:
                    bot.alive = False
                    level3_bots_killed += 1
                    level3_bullets.remove(bullet)
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
        
        if bot.alive and pygame.Rect(bot.x, bot.y, 50, 50).colliderect(pygame.Rect(level3_ship_x, level3_ship_y, 40, 60)):
            if level3_life_count > 0:
                level3_life_count -= 1
            bot.alive = False
        
        for bullet in bot.bullets[:]:
            if pygame.Rect(level3_ship_x, level3_ship_y, 40, 60).colliderect(pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)):
                if level3_life_count > 0:
                    level3_life_count -= 1
                bot.bullets.remove(bullet)
    
    life_text = font.render(f"LIFE: {level3_life_count}", True, WHITE)
    screen.blit(life_text, (20, 20))
    
    kills_text = font.render(f"KILLS: {level3_bots_killed}", True, WHITE)
    screen.blit(kills_text, (20, 70))
    
    level_text = medium_font.render("LEVEL 3", True, YELLOW)
    screen.blit(level_text, (WIDTH - 120, 20))
    
    if level3_bots_killed >= 15:
        victory_text = popup_font.render("LEVEL 3 COMPLETE!", True, GREEN)
        screen.blit(victory_text, victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        continue_text = small_font.render("Click to return to main menu", True, WHITE)
        screen.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

def calculate_score_requirement(dice_value):
    """Calculate score requirement based on dice roll"""
    requirements = {
        1: 10, 2: 200, 3: 50, 4: 100, 5: 30, 6: 500
    }
    return requirements.get(dice_value, 100)

def update_score(points):
    """Update the current score"""
    global current_score
    current_score += points

def check_level3_unlock():
    """Check if player has met the score requirement for level 3"""
    global level3_unlocked
    if level3_dice_rolled and current_score >= level3_score_requirement:
        level3_unlocked = True

def reset_level3_progression():
    """Reset level 3 progression variables"""
    global level3_dice_rolled, level3_dice_number, level3_score_requirement
    global level3_dice_rolling, level3_dice_roll_timer, level3_unlocked, current_score
    level3_dice_rolled = False
    level3_dice_number = None
    level3_score_requirement = 0
    level3_dice_rolling = False
    level3_dice_roll_timer = 0
    level3_unlocked = False
    current_score = 0

def draw_dice_dots(n, rect, dot_radius):
    """Helper function to draw dice dots"""
    cx, cy = rect.center
    offset = 30
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

def draw_level2():
    global life_count, bots_killed, level2_won, current_score
    
    if life_count <= 0:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 100)))
        return
    
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
                    bots_killed += 1
                    update_score(10)
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
        
        if bot.alive and pygame.Rect(bot.x, bot.y, 50, 50).colliderect(pygame.Rect(ship_x, ship_y, 40, 60)):
            if life_count > 0:
                life_count -= 1
            bot.alive = False
        
        for bullet in bot.bullets[:]:
            if pygame.Rect(ship_x, ship_y, 40, 60).colliderect(pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)):
                if life_count > 0:
                    life_count -= 1
                bot.bullets.remove(bullet)
    
    life_text = font.render(f"LIFE: {life_count}", True, WHITE)
    screen.blit(life_text, (20, 20))
    
    score_text = font.render(f"SCORE: {current_score}", True, WHITE)
    screen.blit(score_text, (20, 70))
    
    if bots_killed >= 10:
        level2_won = True
        victory_text = popup_font.render("LEVEL 2 COMPLETE!", True, GREEN)
        screen.blit(victory_text, victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        continue_text = small_font.render("Click to return to level selection", True, WHITE)
        screen.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

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
    draw_dice_dots(n, rect, dot_radius)

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
        victory_text = popup_font.render("LEVEL 1 COMPLETE!", True, GREEN)
        screen.blit(victory_text, victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        continue_text = small_font.render("Click to return to level selection", True, WHITE)
        screen.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    now = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "start" and button_rect.collidepoint(event.pos):
                state = "dice"
                reset_level3_progression()
            elif state == "dice":
                if dice_number and continue_button_rect.collidepoint(event.pos):
                    state = "level_select"
                else:
                    rolling = True
                    roll_timer = pygame.time.get_ticks()
            elif state == "level_select":
                if level1_button_rect.collidepoint(event.pos):
                    initialize_level1()
                    state = "level1"
                elif level2_button_rect.collidepoint(event.pos):
                    initialize_level2()
                    state = "level2"
                elif level3_select_button_rect.collidepoint(event.pos):
                    initialize_level3()
                    state = "level3"
            elif state == "level1" and level_completed:
                state = "level_select"
                level_completed = False
            elif state == "level2" and level2_won:
                state = "level_select"
                level2_won = False
            elif state == "level3" and level3_bots_killed >= 15:
                state = "start"
                reset_level3_progression()
        
        # Level-specific key events
        if state == "level2" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not level2_won:
            bullets.append(Bullet(ship_x + 22, ship_y))
        elif state == "level3" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if level3_life_count > 0 and level3_bots_killed < 15:
                level3_bullets.append(Bullet(level3_ship_x + 22, level3_ship_y))

    # State-specific updates
    if state == "dice":
        draw_dice()
        if rolling and now - roll_timer > 1000:
            dice_number = random.randint(1, 6)
            rolling = False
    elif state == "level_select":
        draw_level_selection()
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
    elif state == "level3":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and level3_ship_x > 0:
            level3_ship_x -= 6
        if keys[pygame.K_RIGHT] and level3_ship_x < WIDTH - 50:
            level3_ship_x += 6
        if keys[pygame.K_UP] and level3_ship_y > 0:
            level3_ship_y -= 6
        if keys[pygame.K_DOWN] and level3_ship_y < HEIGHT - 50:
            level3_ship_y += 6
        draw_level3()
    elif state == "start":
        draw_start()

    pygame.display.flip()
    clock.tick(60)
