import pygame
import sys 
import random 

# initialize 
pygame.init()

#screen setup 
WIDTH, HEIGHT = 800, 600 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DICE")

#colors
WHITE =(255, 255, 255)
BLACK =(0,0,0)

font = pygame.font.SysFont("Arial",50)

#button setup 
button_rect = pygame.Rect(WIDTH//2 -100 , HEIGHT//2 - 40, 200, 80)

# GAME STATE

state = "START"
dice_number = None
rolling = False
roll_timer = 0 


clock = pygame.time.Clock() 

# ------- DRAW FUNCTIONS ---------

def draw_start_screen():
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, button_rect, width=3, border_radius=20)
    pygame.draw.rect(screen, BLACK, button_rect.inflate(-6,-6), border_radius =20)
    text_surface = font.render("START", True, WHITE)
    text_rect = text_surface.get_rect(center = button_rect.center)
    screen.blit(text_surface, text_rect)

def draw_dice_face(number):
    dot_radius = 10
    die_size = 200
    die_rect = pygame.Rect(WIDTH//2 - die_size//2, HEIGHT//2 - die_size//2, die_size, die_size)

    pygame.draw.rect(screen, WHITE, die_rect, border_radius=20)

    cx, cy = die_rect.center
    offset = 40 

    dot_positions = {
        1: [(cx, cy)],
        2: [(cx - offset, cy - offset),(cx + offset, cy + offset)],
        3: [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)],
        4: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx - offset, cy + offset), (cx + offset, cy + offset)],
        5: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx, cy), (cx - offset, cy + offset), (cx + offset, cy + offset)],
        6: [(cx - offset, cy - offset), (cx + offset, cy - offset),
            (cx - offset, cy), (cx + offset, cy), 
            (cx - offset, cy + offset) (cx + offset, cy + offset)]
    }

    for pos in dot_positions[number]:
        pygame.draw.circle(screen, BLACK, pos, dot_radius)

def draw_dice_screen():
    screen.fill(BLACK)
    if rolling:
        rand_face = random.randint(1, 6)
        draw_dice_face(rand_face)
    elif dice_number:
        draw_dice_face(dice_number)
    else:
        draw_dice_face

# ----------- Main GAME loop ------------

running = True 
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if state == "START":
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                state = "DICE"

        elif state == "DICE":
            if event.type == pygame.MOUSEBUTTONDOWN:
                rolling = True
                roll_timer = pygame.time.get_ticks()

    if state == "START":
        draw_start_screen()
    elif state == "DICE":
        draw_dice_screen()
        if rolling:
            now = pygame.time.get_ticks()
            if now - roll_timer > 1000: # 1 sec spin
                dice_number = random.randint(1, 6)
                rolling = False 
    
    pygame.display.flip()
    clock.tick(60)



