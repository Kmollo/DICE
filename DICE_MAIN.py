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

# Font
font = pygame.font.SysFont("Arial", 50)
small_font = pygame.font.SysFont("Arial", 20)
popup_font = pygame.font.SysFont("Arial", 40)
medium_font = pygame.font.SysFont("Arial", 30)

# Load images
try:
    BG = pygame.transform.scale(pygame.image.load("bg.png"), (WIDTH, HEIGHT))
    SPACESHIP_IMAGE = pygame.image.load("spaceship.png")
    SPACESHIP = pygame.transform.scale(SPACESHIP_IMAGE, (40, 60))
    LEVEL2_BG = pygame.transform.scale(pygame.image.load("space1.jpg"), (WIDTH, HEIGHT))
    BOT_IMAGE = pygame.transform.scale(pygame.image.load("bot.png"), (50, 50))
    # Level 3 assets
    LEVEL3_BG = pygame.transform.scale(pygame.image.load("2BG.jpg"), (WIDTH, HEIGHT))
    RED_SPACESHIP_IMAGE = pygame.image.load("Red_space_ship.png")
    RED_SPACESHIP = pygame.transform.scale(RED_SPACESHIP_IMAGE, (40, 60))
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
level2_won = False

# Level 3 progression system
level3_dice_rolled = False
level3_dice_number = None
level3_score_requirement = 0
level3_dice_rolling = False
level3_dice_roll_timer = 0
level3_unlocked = False
current_score = 0  # Track player's current score

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

class Level3EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.width = 4
        self.height = 10

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))  # Blue beams

class Level3Bot:
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
        bullet = Level3EnemyBullet(self.x + 22, self.y + 50)  # Uses blue beams
        self.bullets.append(bullet)

    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, (self.x, self.y))
        for bullet in self.bullets:
            bullet.move()
            bullet.draw(surface)

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

# ============ LEVEL 3 PROGRESSION SYSTEM ============

def calculate_score_requirement(dice_value):
    """Calculate score requirement based on dice roll"""
    requirements = {
        1: 10,     # If dice shows 1, need 10 points
        2: 200,    # If dice shows 2, need 200 points
        3: 50,     # If dice shows 3, need 50 points
        4: 100,    # If dice shows 4, need 100 points
        5: 30,     # If dice shows 5, need 30 points
        6: 500     # If dice shows 6, need 500 points
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
    global level3_ship_x, level3_ship_y, level3_bullets, level3_life_count, level3_bots_killed, level3_bots
    level3_dice_rolled = False
    level3_dice_number = None
    level3_score_requirement = 0
    level3_dice_rolling = False
    level3_dice_roll_timer = 0
    level3_unlocked = False
    current_score = 0
    # Reset level 3 game state
    level3_ship_x, level3_ship_y = WIDTH // 2, HEIGHT - 70
    level3_bullets = []
    level3_life_count = 0
    level3_bots_killed = 0
    level3_bots = []

def initialize_level3():
    """Initialize Level 3 with starting parameters"""
    global level3_ship_x, level3_ship_y, level3_bullets, level3_life_count, level3_bots_killed, level3_bots
    level3_ship_x, level3_ship_y = WIDTH // 2, HEIGHT - 70
    level3_bullets = []
    level3_life_count = dice_number  # Use dice number from initial roll for lives
    level3_bots_killed = 0
    level3_bots = [Level3Bot(random.randint(50, WIDTH - 100), random.randint(-300, -50)) for _ in range(4)]  # More bots for increased difficulty

def draw_level3():
    """Draw Level 3 gameplay"""
    global level3_life_count, level3_bots_killed, level3_ship_x, level3_ship_y
    
    # Check for game over first
    if level3_life_count <= 0:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 100)))
        return
    
    # Draw Level 3 background and red spaceship
    screen.blit(LEVEL3_BG, (0, 0))
    screen.blit(RED_SPACESHIP, (level3_ship_x, level3_ship_y))
    
    # Handle player bullets
    for bullet in level3_bullets[:]:
        bullet.move()
        bullet.draw(screen)
        if bullet.y < 0:
            level3_bullets.remove(bullet)
    
    # Handle bots
    for bot in level3_bots:
        if bot.alive:
            bot.move()
            if random.randint(0, 100) < 3:  # Slightly higher shooting frequency
                bot.shoot()
            
            # Check bullet collisions with bots
            for bullet in level3_bullets[:]:
                if bot.x < bullet.x < bot.x + 50 and bot.y < bullet.y < bot.y + 50:
                    bot.alive = False
                    level3_bots_killed += 1
                    level3_bullets.remove(bullet)
        else:
            # Respawn bot
            bot.x = random.randint(50, WIDTH - 100)
            bot.y = -60
            bot.alive = True
            bot.bullets.clear()
        
        # Reset bot if it goes off screen
        if bot.y > HEIGHT:
            bot.x = random.randint(50, WIDTH - 100)
            bot.y = -60
            bot.bullets.clear()
        
        bot.draw(screen)
        
        # Check collision with player
        if bot.alive and pygame.Rect(bot.x, bot.y, 50, 50).colliderect(pygame.Rect(level3_ship_x, level3_ship_y, 40, 60)):
            if level3_life_count > 0:
                level3_life_count -= 1
            bot.alive = False
        
        # Check enemy bullet collisions with player
        for bullet in bot.bullets[:]:
            if pygame.Rect(level3_ship_x, level3_ship_y, 40, 60).colliderect(pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)):
                if level3_life_count > 0:
                    level3_life_count -= 1
                bot.bullets.remove(bullet)
    
    # Display UI
    life_text = font.render(f"LIFE: {level3_life_count}", True, WHITE)
    screen.blit(life_text, (20, 20))
    
    kills_text = font.render(f"KILLS: {level3_bots_killed}", True, WHITE)
    screen.blit(kills_text, (20, 70))
    
    level_text = font.render("LEVEL 3", True, YELLOW)
    screen.blit(level_text, (WIDTH - 150, 20))
    
    # Check win condition (example: kill 15 bots)
    if level3_bots_killed >= 15:
        win_text = popup_font.render("LEVEL 3 COMPLETE! You Win!", True, GREEN)
        screen.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

def draw_level3_requirement_dice():
    """Draw the dice roll for level 3 requirements"""
    screen.fill(VBlue)
    
    # Title
    title_text = popup_font.render("Level 3 Requirement Roll", True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150)))
    
    # Dice
    dot_radius = 10
    die_size = 150
    rect = pygame.Rect(WIDTH // 2 - die_size // 2, HEIGHT // 2 - die_size // 2, die_size, die_size)
    pygame.draw.rect(screen, WHITE, rect, border_radius=20)
    
    if level3_dice_rolling:
        draw_dice_dots(random.randint(1, 6), rect, dot_radius)
    elif level3_dice_number:
        draw_dice_dots(level3_dice_number, rect, dot_radius)
        
        # Show requirement
        req_text = medium_font.render(f"Score Required: {level3_score_requirement}", True, WHITE)
        screen.blit(req_text, req_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))
        
        current_score_text = medium_font.render(f"Current Score: {current_score}", True, YELLOW)
        screen.blit(current_score_text, current_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130)))
        
        if level3_unlocked:
            unlock_text = medium_font.render("LEVEL 3 UNLOCKED! Click to continue", True, GREEN)
            screen.blit(unlock_text, unlock_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 170)))
        else:
            need_text = small_font.render("Keep playing Level 2 to reach the requirement!", True, WHITE)
            screen.blit(need_text, need_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 170)))
    else:
        draw_dice_dots(1, rect, dot_radius)
        instruction_text = small_font.render("Click to roll for Level 3 requirement", True, WHITE)
        screen.blit(instruction_text, instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))

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

# ============ EXISTING FUNCTIONS (MODIFIED) ============

def draw_level2_popup():
    if not level3_dice_rolled:
        text = popup_font.render("Level 2 Complete! Roll for Level 3", True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        instruction_text = small_font.render("Click to roll dice for Level 3 requirement", True, WHITE)
        screen.blit(instruction_text, instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
    else:
        if level3_unlocked:
            text = popup_font.render("Ready for Level 3! Click to continue", True, GREEN)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        else:
            text = popup_font.render(f"Need {level3_score_requirement - current_score} more points!", True, YELLOW)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            instruction_text = small_font.render("Keep playing to reach the requirement", True, WHITE)
            screen.blit(instruction_text, instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

def draw_level2():
    global life_count, bots_killed, level2_won, current_score
    
    # Check for game over first to determine background
    if life_count <= 0:
        # Game Over - black background
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 100)))
        return
    
    # Normal gameplay - draw background and game elements
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
                    update_score(10)  # Add 10 points per bot killed
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
    
    # Display UI
    life_text = font.render(f"LIFE: {life_count}", True, WHITE)
    screen.blit(life_text, (20, 20))
    
    score_text = font.render(f"SCORE: {current_score}", True, WHITE)
    screen.blit(score_text, (20, 70))
    
    if level3_dice_rolled:
        req_text = small_font.render(f"Level 3 Req: {level3_score_requirement}", True, YELLOW)
        screen.blit(req_text, (20, 120))
    
    if bots_killed >= 10:
        level2_won = True
        check_level3_unlock()  # Check if level 3 is unlocked
        draw_level2_popup()

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
        text = popup_font.render("Press any key for Level 2", True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

# ============ MAIN GAME LOOP ============

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
                reset_level3_progression()  # Reset progression when starting new game
            elif state == "level2" and level2_won:
                if not level3_dice_rolled:
                    # Start dice roll for level 3 requirement
                    state = "level3_dice"
                elif level3_unlocked:
                    # Proceed to level 3
                    initialize_level3()
                    state = "level3"
            elif state == "level3_dice":
                if not level3_dice_rolling and not level3_dice_rolled:
                    # Start rolling
                    level3_dice_rolling = True
                    level3_dice_roll_timer = now
                elif level3_dice_rolled and level3_unlocked:
                    # Continue to level 3
                    initialize_level3()
                    state = "level3"
                elif level3_dice_rolled and not level3_unlocked:
                    # Return to level 2 to continue scoring
                    state = "level2"
                    level2_won = False
        
        if state == "dice":
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
        elif state == "level1" and event.type == pygame.KEYDOWN and level_completed:
            life_count = dice_number
            current_score = 0  # Reset score for level 2
            state = "level2"
        elif state == "level2" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not level2_won:
            bullets.append(Bullet(ship_x + 22, ship_y))
        elif state == "level3" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and level3_life_count > 0:
            level3_bullets.append(Bullet(level3_ship_x + 22, level3_ship_y))

    # State-specific updates
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
    elif state == "level3":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and level3_ship_x > 0:
            level3_ship_x -= 5
        if keys[pygame.K_RIGHT] and level3_ship_x < WIDTH - 50:
            level3_ship_x += 5
        if keys[pygame.K_UP] and level3_ship_y > 0:
            level3_ship_y -= 5
        if keys[pygame.K_DOWN] and level3_ship_y < HEIGHT - 50:
            level3_ship_y += 5
        draw_level3()
    elif state == "level3_dice":
        if level3_dice_rolling and now - level3_dice_roll_timer > 1000:
            level3_dice_number = random.randint(1, 6)
            level3_score_requirement = calculate_score_requirement(level3_dice_number)
            level3_dice_rolling = False
            level3_dice_rolled = True
            check_level3_unlock()
        draw_level3_requirement_dice()
    elif state == "start":
        draw_start()

    pygame.display.flip()
    clock.tick(60) 
