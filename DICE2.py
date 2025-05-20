import pygame
import sys
import random
import time

# Initialize
pygame.init()
pygame.font.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dice")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 225)
VBlue = (50, 74, 178)
RED = (255, 0, 0)

# Font
font = pygame.font.SysFont("Arial", 50)
small_font = pygame.font.SysFont("Arial", 20)

# Button setup
button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 80)
continue_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 60)

# Game state
state = "start"
dice_number = None
rolling = False
roll_timer = 0
player_lives = 0

# space game setup
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_VEL = 5
player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT - 50, PLAYER_WIDTH, PLAYER_HEIGHT)
beams = []
BEAM_COOLDOWN = 1000
beam_timer = 0

# Load images
try:
    BG = pygame.transform.scale(pygame.image.load("bg.png"), (WIDTH, HEIGHT))
    SPACESHIP_IMAGE = pygame.image.load("spaceship.png")
    SPACESHIP = pygame.transform.scale(SPACESHIP_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))
except Exception as e:
    print("Image loading error:", e)
    pygame.quit()
    sys.exit()

clock = pygame.time.Clock()

# ----------- DRAW FUNCTIONS -----------

def draw_start_screen():
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, button_rect, width=3, border_radius=20)
    pygame.draw.rect(screen, BLUE, button_rect.inflate(-6, -6), border_radius=20)
    text_surface = font.render("START", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

def draw_dice_face(number):
    dot_radius = 10
    die_size = 200
    die_rect = pygame.Rect(WIDTH // 2 - die_size // 2, HEIGHT // 2 - die_size // 2, die_size, die_size)

    pygame.draw.rect(screen, WHITE, die_rect, border_radius=20)
    cx, cy = die_rect.center
    offset = 40

    dot_positions = {
        1: [(cx, cy)],
        2: [(cx - offset, cy - offset), (cx + offset, cy + offset)],
        3: [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)],
        4: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx - offset, cy + offset), (cx + offset, cy + offset)],
        5: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx, cy), (cx - offset, cy + offset), (cx + offset, cy + offset)],
        6: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx - offset, cy), (cx + offset, cy),
            (cx - offset, cy + offset), (cx + offset, cy + offset)]
    }

    for pos in dot_positions[number]:
        pygame.draw.circle(screen, BLACK, pos, dot_radius)

def draw_dice_screen():
    screen.fill(BLUE)
    if rolling:
        rand_face = random.randint(1, 6)
        draw_dice_face(rand_face)
    elif dice_number:
        draw_dice_face(dice_number)
        pygame.draw.rect(screen, WHITE, continue_button_rect, border_radius=15)
        text_surface = small_font.render("CONTINUE", True, BLACK)
        text_rect = text_surface.get_rect(center=continue_button_rect.center)
        screen.blit(text_surface, text_rect)
    else:
        draw_dice_face(1)

def draw_play_screen():
    screen.fill(WHITE)
    for i in range(player_lives):
        pygame.draw.circle(screen, RED, (30 + i * 40, 30), 15)
    ground_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
    pygame.draw.rect(screen, BLACK, ground_rect)

def draw_space_screen():
    screen.blit(BG, (0, 0))
    screen.blit(SPACESHIP, (player.x, player.y))
    for beam in beams:
        pygame.draw.rect(screen, RED, beam)

# ----------- MAIN GAME LOOP -----------

running = True
start_time = 0
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
                if dice_number is not None and continue_button_rect.collidepoint(event.pos):
                    state = "space"
                    player_lives = dice_number
                    beams = []
                    start_time = pygame.time.get_ticks()
                    beam_timer = start_time
                else:
                    rolling = True
                    roll_timer = pygame.time.get_ticks()

    if state == "start":
        draw_start_screen()
    elif state == "dice":
        draw_dice_screen()
        if rolling and now - roll_timer > 1000:
            dice_number = random.randint(1, 6)
            rolling = False
    elif state == "space":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL

        if now - beam_timer > BEAM_COOLDOWN:
            beam_x = random.randint(0, WIDTH - 10)
            beams.append(pygame.Rect(beam_x, 0, 10, 30))
            beam_timer = now

        for beam in beams[:]:
            beam.y += 5
            if beam.colliderect(player):
                beams.remove(beam)
                player_lives -= 1
                if player_lives <= 0:
                    print("Game Over")
                    pygame.quit()
                    sys.exit()

        draw_space_screen()

    pygame.display.flip()
    clock.tick(60)
