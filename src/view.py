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

        title_text = self.font.render("---BLACKMARKET---", False, COLOR_TEXT)
        self.screen.blit(title_text, (20, 20))
        y_offset = 70
        for category in economy.market.categories.values():
            price_str = f"{category.name}: ${category.current_price:.2f}"
            text_surface = self.font.render(price_str, False, COLOR_TEXT)
            self.screen.blit(text_surface, (20, y_offset))

            price_range = category.max_price - category.min_price
            current_progress = category.current_price - category.min_price

            fill_percentage = 0
            if price_range > 0:
                fill_percentage = max(0.0, min(1.0, current_progress / price_range))

            bar_width = market_width - 40
            bar_height = 15
            fill_width = int(bar_width * fill_percentage)

            pygame.draw.rect(self.screen, COLOR_BORDER, (20, y_offset + 30, bar_width, bar_height), 1)
            pygame.draw.rect(self.screen, COLOR_TEXT, (20, y_offset + 30, fill_width, bar_height))

            y_offset += 80

        pygame.draw.rect(self.screen, COLOR_PANEL, (market_width, 0, server_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (market_width, 0, server_width, SCREEN_HEIGHT), 2)

        finance_x = market_width + server_width
        pygame.draw.rect(self.screen, COLOR_PANEL, (finance_x, 0, finance_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (finance_x, 0, finance_width, SCREEN_HEIGHT), 2)

        balance_text = self.font.render(f"Balance: ${economy.balance:.2f}", False, (0, 255, 0))
        self.screen.blit(balance_text, (finance_x + 20, 20))

        pygame.display.flip()