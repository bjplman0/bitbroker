import pygame
import sys
import settings

def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    pygame.display.set_caption(settings.WINDOW_TITLE)
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
        screen.fill(settings.COLOR_BG)
        pygame.display.flip()
        clock.tick(settings.FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()