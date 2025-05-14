import pygame 
import sys
 


pygame.init()

#screen setup 

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DICE")


# Colors
WHITE = (255, 255, 255)
BLACK = (0,0,0)

# fONT 
font = pygame.font.SysFont("ARial", 50)

button_rect = pygame.Rect(WIDTH//2 -100, HEIGHT//2 - 40, 200, 80)

# game loop
running =True
while running:
    screen.fill(BLACK)

    # Draw Button (rounded corners with border)
    pygame.draw.rect(screen, WHITE, button_rect, width=3, border_bottom_left_radius=20)
    pygame.draw.rect(screen, BLACK, button_rect.inflate(-6,-6), border_radius=28)

    # Draw text
    text_surface = font.render("START", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        

        # detect click on button 
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                print("GAME STARTS!")

    
    pygame.display.flip()


