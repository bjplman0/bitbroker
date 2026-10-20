import pygame
from settings import *
from model import ServerState

class GameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE)
        self.font_small = pygame.font.Font(FONT_PATH, FONT_SIZE_SMALL)

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

    def _draw_panel_title(self, text, start_x):
        title_text = self.font.render(text, False, COLOR_TEXT)
        self.screen.blit(title_text, (start_x + 20, 20))

    def _draw_market_panel(self, market, start_x, width):
        self._draw_panel_bg(start_x, width)
        self._draw_panel_title("---BLACKMARKET---", start_x)
        
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
        self._draw_panel_title("---SERVERPARK---", start_x)

        y_offset = 100
        rack_height = 150
        rack_padding = 20
        card_width = width - 40

        state_colors = {
            ServerState.IDLE: COLOR_IDLE,
            ServerState.WORKING: COLOR_WORKING,
            ServerState.OVERHEATED: COLOR_OVERHEAT
        }

        for server in servers:
            rect = pygame.Rect(start_x + 20, y_offset, card_width, rack_height)
            color = state_colors[server.state]

            pygame.draw.rect(self.screen, COLOR_PANEL_LIGHT, rect, border_radius=CARD_RADIUS)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius = CARD_RADIUS)

            self._draw_server_header(server, rect, color)
            self._draw_temp_bar(server, rect, color)
            self._draw_progress_bar(server, rect)

            y_offset += rack_height + rack_padding

    def _draw_server_header(self, server, rect, color):
        name_text = self.font.render(server.name, False, COLOR_TEXT)
        self.screen.blit(name_text, (rect.x + 15, rect.y + 12))

        status_text = self.font_small.render(server.state.name, False, color)
        status_x = rect.right - status_text.get_width() - 15
        self.screen.blit(status_text, (status_x, rect.y + 18))

        if server.state == ServerState.WORKING and server.current_job:
            job_text = self.font_small.render(
                f"Job: {server.current_job.name}", False, COLOR_TEXT_DIM
            )
            self.screen.blit(job_text, (rect.x + 15, rect.y + 45))

    def _draw_temp_bar(self, server, rect, color):
        label = self.font_small.render("TEMP", False, COLOR_TEXT_DIM)
        self.screen.blit(label, (rect.x + 15, rect.y + 75))

        bar_rect = pygame.Rect(rect.x + 70, rect.y + 78, rect.width - 170, 16)
        temp_range = server.max_temperature - SERVER_BASE_TEMP
        current = server.temperature - SERVER_BASE_TEMP
        pct = max(0.0, min(1.0, current / temp_range)) if temp_range > 0 else 0.0

        self._draw_bar(bar_rect, pct, color)

        value_text = self.font_small.render(f"{server.temperature:.1f}C", False, color)
        self.screen.blit(value_text, (bar_rect.right + 10, bar_rect.y - 1))

    def _draw_progress_bar(self, server, rect):
        label = self.font_small.render("PROG", False, COLOR_TEXT_DIM)
        self.screen.blit(label, (rect.x + 15, rect.y + 105))

        bar_rect = pygame.Rect(rect.x + 70, rect.y + 108, rect.width - 170, 16)

        if server.state == ServerState.WORKING and server.current_job:
            pct = 1.0 - (server.current_job.remaining_work / server.current_job.total_work)
        else:
            pct = 0.0

        self._draw_bar(bar_rect, pct, COLOR_TEXT)

    def _draw_bar(self, rect, pct, fill_color):
        pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 1, border_radius=4)

        if pct > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, int(rect.width * pct), rect.height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=4)

    def _draw_finance_panel(self, economy, start_x, width):
        self._draw_panel_bg(start_x, width)

        # title
        balance_text = self.font.render(f"Balance: ${economy.balance:.2f}", False, COLOR_TEXT)
        self.screen.blit(balance_text, (start_x + 20, 20))