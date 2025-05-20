import pygame 
import time 
import random 

# initialize font 
pygame.font.init()

#window dimensions 
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Race")

# Player info 
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_VEL = 5

# Load assets
BG = pygame.transform.scale(pygame.image.load("bg.png"), (WIDTH, HEIGHT))
SPACESHIP_IMAGE = pygame.image.load("spaceship.png")
SPACESHIP = pygame.transform.scale(SPACESHIP_IMAGE, (PLAYER_WIDTH, PLAYER_WIDTH))

# Font for timer 
FONT = pygame.font.SysFont("Arial", 30)

# Draw function
def draw(player, elapsed_time):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}", 1, "white")
    WIN.blit(time_text, (10, 10))

    WIN.blit(SPACESHIP, (player.x, player.y))

    pygame.display.update()

# main game loop
def main():
    run = True

    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0 
    while run:
        clock.tick(60)
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
                break 
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        
        draw(player, elapsed_time)

    pygame.quit()

if __name__ == "__main__":
    main()