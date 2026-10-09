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

        market_w = int(SCREEN_WIDTH * 0.3)
        server_w = int(SCREEN_WIDTH * 0.5)
        finance_w = int(SCREEN_WIDTH * 0.2)

        self._draw_market_panel(economy.market, 0, market_w)
        self._draw_server_panel(economy.servers, market_w, server_w)
        self._draw_finance_panel(economy, market_w + server_w, finance_w)

        pygame.display.flip()

    def _draw_panel_bg(self, start_x, width):
        pygame.draw.rect(self.screen, COLOR_PANEL, (start_x, 0, width, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (start_x, 0, width, SCREEN_HEIGHT), 2)

    def _draw_market_panel(self, market, start_x, width):

        self._draw_panel_bg(start_x, width)

        title_text = self.font.render("---BLACKMARKET---", False, COLOR_TEXT)
        self.screen.blit(title_text, (start_x + 20, 20))
        
        y_offset = 100

        for category in market.categories.values():
            price_str = f"{category.name}: ${category.current_price:,.0f}"
            text_surface = self.font.render(price_str, False, COLOR_TEXT)
            self.screen.blit(text_surface, (start_x + 20, y_offset))

            graph_width = width - 40
            graph_height = 80
            graph_rect = pygame.Rect(start_x + 20, y_offset + 40, graph_width, graph_height)
            pygame.draw.rect(self.screen, COLOR_BORDER, graph_rect, 1)

            if len(category.price_history) > 1:
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

    def _draw_server_panel(self, servers, start_x, width):

        self._draw_panel_bg(start_x, width)

        title_text = self.font.render("---SERVERPARK---", False, COLOR_TEXT)
        self.screen.blit(title_text, (start_x + 20, 20))

    def _draw_finance_panel(self, economy, start_x, width):

        self._draw_panel_bg(start_x, width)

        balance_text = self.font.render(f"Balance: ${economy.balance:.2f}", False, COLOR_TEXT)
        self.screen.blit(balance_text, (start_x + 20, 20))