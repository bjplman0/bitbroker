import pygame
from settings import *

class GameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE)

    def draw(self, economy):
        self.screen.fill(COLOR_BG)

        market_width = int(SCREEN_WIDTH * 0.3)
        server_width = int(SCREEN_WIDTH * 0.5)
        finance_width = int(SCREEN_WIDTH * 0.2)

        pygame.draw.rect(self.screen, COLOR_PANEL, (0, 0, market_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (0, 0, market_width, SCREEN_HEIGHT), 2)

        pygame.draw.rect(self.screen, COLOR_PANEL, (market_width, 0, server_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (market_width, 0, server_width, SCREEN_HEIGHT), 2)

        finance_x = market_width + server_width
        pygame.draw.rect(self.screen, COLOR_PANEL, (finance_x, 0, finance_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (finance_x, 0, finance_width, SCREEN_HEIGHT), 2)

        balance_text = self.font.render(f"Balance: ${economy.balance:.2f}", False, (0, 255, 0))
        self.screen.blit(balance_text, (finance_x + 20, 20))

        pygame.display.flip()