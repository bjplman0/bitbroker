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
        y_offset = 100

        for category in economy.market.categories.values():

            price_str = f"{category.name}: {category.current_price:,.0f} CR"
            text_surface = self.font.render(price_str, False, COLOR_TEXT)
            self.screen.blit(text_surface, (20, y_offset))

            graph_width = market_width - 40
            graph_height = 80
            graph_rect = pygame.Rect(20, y_offset + 40, graph_width, graph_height)
            pygame.draw.rect(self.screen, COLOR_BORDER, graph_rect, 1)

            if hasattr(category, 'price_history') and len(category.price_history) > 1:
                points = []
                
                local_min = min(category.price_history)
                local_max = max(category.price_history)
                
                if local_max == local_min:
                    local_max += 10
                    local_min -= 10
                
                padding = (local_max - local_min) * 0.1
                display_max = local_max + padding
                display_min = local_min - padding
                price_range = display_max - display_min

                for i, past_price in enumerate(category.price_history):
                    px = graph_rect.x + (i / (category.history_length - 1)) * graph_width
                    
                    normalized_y = (past_price - display_min) / price_range
                    
                    py = graph_rect.y + graph_rect.height - (normalized_y * graph_rect.height)
                    points.append((px, py))

                pygame.draw.aalines(self.screen, COLOR_TEXT, False, points)

            y_offset += 170

        pygame.draw.rect(self.screen, COLOR_PANEL, (market_width, 0, server_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (market_width, 0, server_width, SCREEN_HEIGHT), 2)

        finance_x = market_width + server_width
        pygame.draw.rect(self.screen, COLOR_PANEL, (finance_x, 0, finance_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (finance_x, 0, finance_width, SCREEN_HEIGHT), 2)

        balance_text = self.font.render(f"Balance: ${economy.balance:.2f}", False, (0, 255, 0))
        self.screen.blit(balance_text, (finance_x + 20, 20))

        pygame.display.flip()