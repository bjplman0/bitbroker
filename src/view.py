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
        self.tab_rects = {}
        self.hitboxes = []
        self.renderers = {
            "dashboard": self._draw_dashboard,
            "marketplace": self._draw_marketplace,
            "financial": self._draw_financial,
        }

    def draw(self, economy, states, active_tab_key, mouse_pos, paused=False):
        self.screen.fill(COLOR_BG)
        self.hitboxes.clear()

        tabs = {key: state.label for key, state in states.items()}
        self._draw_tab_bar(tabs, active_tab_key)

        self.renderers[active_tab_key](economy, mouse_pos, states[active_tab_key])

        if economy.game_over:
            self._draw_game_over(economy, mouse_pos)
        elif paused:
            self._draw_pause_menu(mouse_pos)
            
        pygame.display.flip()

    def draw_main_menu(self, mouse_pos, can_continue):
        self.screen.fill(COLOR_BG)
        self.hitboxes.clear()

        w, h = self.screen.get_size()
        pygame.draw.rect(self.screen, COLOR_PANEL, (0, 0, w, h))
        pygame.draw.rect(self.screen, COLOR_BORDER, (0, 0, w, h), 2)

        box = pygame.Rect(0, 0, MENU_BOX_WIDTH, MENU_BOX_HEIGHT)
        box.center = (w // 2, h // 2)
        pygame.draw.rect(self.screen, COLOR_PANEL_LIGHT, box, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_BORDER, box, 2, border_radius=CARD_RADIUS)

        title_surf = self.font.render("---BITBROKER---", False, COLOR_TEXT)
        self.screen.blit(title_surf, title_surf.get_rect(midtop=(box.centerx, box.y + 45)))

        subtitle_surf = self.font_small.render("SERVER PARK MANAGEMENT SIMULATION", False, COLOR_TEXT_DIM)
        self.screen.blit(subtitle_surf, subtitle_surf.get_rect(midtop=(box.centerx, box.y + 90)))

        buttons = [
            ("NEW GAME", "menu_new", True),
            ("CONTINUE", "menu_continue", can_continue),
            ("QUIT", "menu_quit", True),
        ]

        y = box.y + 150
        for label_text, kind, enabled in buttons:
            btn = pygame.Rect(0, 0, MENU_BTN_WIDTH, MENU_BTN_HEIGHT)
            btn.midtop = (box.centerx, y)

            if enabled:
                self._add_hitbox(btn, kind, None)
                if btn.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn, border_radius=CARD_RADIUS)
                border_color = COLOR_TEXT
                text_color = COLOR_TEXT
            else:
                border_color = COLOR_TEXT_DIM
                text_color = COLOR_TEXT_DIM

            pygame.draw.rect(self.screen, border_color, btn, 2, border_radius=CARD_RADIUS)
            lbl = self.font.render(label_text, False, text_color)
            self.screen.blit(lbl, lbl.get_rect(center=btn.center))
            y += MENU_BTN_HEIGHT + MENU_BTN_GAP

        pygame.display.flip()

    def _draw_pause_menu(self, mouse_pos):
        self.hitboxes.clear()

        w, h = self.screen.get_size()
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, OVERLAY_ALPHA))
        self.screen.blit(shade, (0, 0))

        box = pygame.Rect(0, 0, PAUSE_BOX_WIDTH, PAUSE_BOX_HEIGHT)
        box.center = (w // 2, h // 2)
        pygame.draw.rect(self.screen, COLOR_PANEL, box, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_BORDER, box, 3, border_radius=CARD_RADIUS)

        title = self.font.render("--PAUSED--", False, COLOR_TEXT)
        self.screen.blit(title, title.get_rect(midtop=(box.centerx, box.y + 40)))

        buttons = [
            ("RETURN TO GAME [ESC]", "pause_resume"),
            ("SAVE & QUIT TO MENU", "pause_save_quit"),
        ]

        y = box.y + 115
        for label_text, kind in buttons:
            btn = pygame.Rect(0, 0, PAUSE_BTN_WIDTH, PAUSE_BTN_HEIGHT)
            btn.midtop = (box.centerx, y)
            self._add_hitbox(btn, kind, None)

            if btn.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn, border_radius=CARD_RADIUS)
            pygame.draw.rect(self.screen, COLOR_TEXT, btn, 2, border_radius=CARD_RADIUS)

            lbl = self.font.render(label_text, False, COLOR_TEXT)
            self.screen.blit(lbl, lbl.get_rect(center=btn.center))
            y += PAUSE_BTN_HEIGHT + MENU_BTN_GAP

    def _add_hitbox(self, rect, kind, obj):
        self.hitboxes.append({"rect": rect, "kind": kind, "obj": obj})

    def get_hit(self, pos):
        for hb in reversed(self.hitboxes):
            if hb["rect"].collidepoint(pos):
                return (hb["kind"], hb["obj"])
        return None

    def _draw_dashboard(self, economy, mouse_pos, state):
        w = self.screen.get_width()
        market_w = int(w * DASHBOARD_MARKET_RATIO)
        server_w = int(w * DASHBOARD_SERVER_RATIO)
        finance_w = int(w * DASHBOARD_FINANCE_RATIO)

        self._draw_market_panel(economy.market, 0, market_w)
        self._draw_server_panel(economy.servers, market_w, server_w, mouse_pos, state.selected_job)
        self._draw_finance_panel(economy, market_w + server_w, finance_w, mouse_pos, state.selected_job)

    def _draw_marketplace(self, economy, mouse_pos, state):
        panel_w = self.screen.get_width()
        self._draw_panel_bg(0, panel_w)
        self._draw_panel_title("---JOB MARKET---", 0)

        count_str = f"{len(economy.job_market)}/{economy.job_generator.pool_max_size}"
        count_surf = self.font.render(count_str, False, COLOR_TEXT_DIM)
        self.screen.blit(count_surf, (panel_w - TABLE_MARGIN - count_surf.get_width(), TAB_BAR_HEIGHT + PANEL_PADDING))

        table_x = TABLE_MARGIN
        table_w = panel_w - 2 * TABLE_MARGIN
        y = TAB_BAR_HEIGHT + 90

        for text, frac, align in JOB_COLUMNS:
            self._blit_cell(self.font_small, text, COLOR_TEXT_DIM,
                            table_x + 10, table_w - 20, frac, align, y)
        y += 30
        pygame.draw.line(self.screen, COLOR_BORDER, (table_x, y), (table_x + table_w, y), 2)
        y += 4

        if not economy.job_market:
            empty = self.font.render("No jobs available right now...", False, COLOR_TEXT_DIM)
            self.screen.blit(empty, (table_x + 10, y + 20))
            y += ROW_HEIGHT
        else:
            for job in economy.job_market:
                row_rect = pygame.Rect(table_x, y, table_w, ROW_HEIGHT)
                self._add_hitbox(row_rect, "job", job)

                if row_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, COLOR_ROW_HOVER, row_rect)

                cost_color = COLOR_TEXT if economy.balance >= job.cost else COLOR_OVERHEAT
                profit, pct = economy.expected_profit(job)
                profit_color = COLOR_TEXT if profit >= 0 else COLOR_OVERHEAT
                sign = "+" if profit >= 0 else "-"
                profit_str = f"{sign}${abs(profit):,.0f} ({sign}{abs(pct):.0f}%)"

                values = [
                    (job.name, COLOR_TEXT),
                    (job.data_type, COLOR_TEXT),
                    (f"{job.total_work:,.0f}", COLOR_TEXT),
                    (f"${job.cost:,.0f}", cost_color),
                    (profit_str, profit_color),
                    (f"{job.time_left:.0f}s",
                     COLOR_OVERHEAT if job.time_left < JOB_EXPIRY_WARN_SEC else COLOR_TEXT_DIM),
                ]
                for (_, frac, align), (value, color) in zip(JOB_COLUMNS, values):
                    self._blit_cell(self.font, value, color,
                                    table_x + 10, table_w - 20, frac, align, y + 8)

                pygame.draw.line(self.screen, COLOR_BORDER,
                                 (table_x, row_rect.bottom), (table_x + table_w, row_rect.bottom), 1)
                y += ROW_HEIGHT
        y += SECTION_GAP_LARGE
        self._draw_server_shop(economy, mouse_pos, table_x, table_w, y)

    def _draw_server_shop(self, economy, mouse_pos, table_x, table_w, y):
        title = self.font.render("---SERVER SHOP---", False, COLOR_TEXT)
        self.screen.blit(title, (table_x, y))

        count_surf = self.font.render(f"{len(economy.servers)}/{MAX_SERVERS}", False, COLOR_TEXT_DIM)
        self.screen.blit(count_surf, (table_x + table_w - count_surf.get_width(), y))
        y += 50

        for text, frac, align in SHOP_COLUMNS:
            self._blit_cell(self.font_small, text, COLOR_TEXT_DIM,
                            table_x + 10, table_w - 20, frac, align, y)
        y += 30
        pygame.draw.line(self.screen, COLOR_BORDER, (table_x, y), (table_x + table_w, y), 2)
        y += 4

        park_full = len(economy.servers) >= MAX_SERVERS

        for offer in SERVER_CATALOG:
            row_rect = pygame.Rect(table_x, y, table_w, ROW_HEIGHT)
            self._add_hitbox(row_rect, "server_offer", offer)

            affordable = economy.balance >= offer["capex"]
            if affordable and not park_full and row_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, COLOR_ROW_HOVER, row_rect)

            text_color = COLOR_TEXT_DIM if park_full else COLOR_TEXT
            cost_color = COLOR_TEXT if affordable else COLOR_OVERHEAT

            values = [
                (offer["model"], text_color),
                (f"{offer['processing_speed']:.0f}", text_color),
                (f"{offer['max_temperature']:.0f}C", text_color),
                (f"${offer['opex']:,.0f}/s", text_color),
                (f"${offer['capex']:,.0f}", cost_color),
            ]
            for (_, frac, align), (value, color) in zip(SHOP_COLUMNS, values):
                self._blit_cell(self.font, value, color,
                                table_x + 10, table_w - 20, frac, align, y + 8)

            pygame.draw.line(self.screen, COLOR_BORDER,
                             (table_x, row_rect.bottom), (table_x + table_w, row_rect.bottom), 1)
            y += ROW_HEIGHT

    def _blit_cell(self, font, text, color, table_x, table_w, frac, align, y):
        surf = font.render(text, False, color)
        x = table_x + int(table_w * frac)
        if align == "right":
            x -= surf.get_width()
        self.screen.blit(surf, (x, y))

    def _draw_tab_bar(self, tabs, active_tab_key):
        pygame.draw.rect(self.screen, COLOR_PANEL, (0, 0, SCREEN_WIDTH, TAB_BAR_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_BORDER, (0, 0, SCREEN_WIDTH, TAB_BAR_HEIGHT), 2)

        self.tab_rects = {}
        x = PANEL_PADDING

        for key, label in tabs.items():
            is_active = (key == active_tab_key)
            color = COLOR_TEXT if is_active else COLOR_TEXT_DIM

            text_surface = self.font.render(label, False, color)
            text_rect = text_surface.get_rect(topleft=(x, 12))
            self.screen.blit(text_surface, text_rect)

            self.tab_rects[key] = text_rect

            x += text_rect.width + TAB_ITEM_SPACING

    def _draw_panel_bg(self, start_x, width):
        panel_rect = pygame.Rect(start_x, TAB_BAR_HEIGHT, width, SCREEN_HEIGHT - TAB_BAR_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, panel_rect, 2)

    def _draw_panel_title(self, text, start_x):
        title_text = self.font.render(text, False, COLOR_TEXT)
        self.screen.blit(title_text, (start_x + PANEL_PADDING, TAB_BAR_HEIGHT + PANEL_PADDING))

    def _draw_market_panel(self, market, start_x, width):
        self._draw_panel_bg(start_x, width)
        self._draw_panel_title("---BLACKMARKET---", start_x)

        y = TAB_BAR_HEIGHT + 80

        for category in market.categories.values():
            rect = pygame.Rect(start_x + PANEL_PADDING, y, width - 2 * PANEL_PADDING, MARKET_CARD_HEIGHT)
            self._draw_price_card(category, rect)
            y += MARKET_CARD_HEIGHT + MARKET_CARD_GAP

    def _draw_dashed_hline(self, color, x1, x2, y, dash=DASH_LENGTH, gap=DASH_GAP):
        y = int(y)
        x = int(x1)
        while x < x2:
            pygame.draw.line(self.screen, color, (x, y), (min(x + dash, int(x2)), y), 1)
            x += dash + gap

    def _draw_price_card(self, category, rect):
        history = category.price_history
        price = category.current_price
        base = category.base_price

        pygame.draw.rect(self.screen, COLOR_PANEL_LIGHT, rect, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 2, border_radius=CARD_RADIUS)

        price_color = COLOR_TEXT if price >= base else COLOR_WARN

        name_surf = self.font.render(category.name, False, COLOR_TEXT)
        self.screen.blit(name_surf, (rect.x + 15, rect.y + 8))
        price_surf = self.font.render(f"${price:,.0f}", False, price_color)
        self.screen.blit(price_surf, (rect.right - price_surf.get_width() - 15, rect.y + 8))

        plot = pygame.Rect(rect.x + 15, rect.y + 50, rect.width - 30, rect.height - 50 - 14)
        pygame.draw.rect(self.screen, COLOR_BORDER, plot, 1)

        n = len(history)
        if n < 2:
            return

        lo = min(min(history), base)
        hi = max(max(history), base)
        min_span = base * MARKET_MIN_SPAN_RATIO
        if hi - lo < min_span:
            mid = (hi + lo) / 2
            lo, hi = mid - min_span / 2, mid + min_span / 2
        pad = (hi - lo) * MARKET_CHART_PAD_RATIO
        lo -= pad
        hi += pad

        def to_px(i, v):
            return (plot.x + i / (n - 1) * plot.width,
                    plot.bottom - (v - lo) / (hi - lo) * plot.height)

        _, base_y = to_px(0, base)
        self._draw_dashed_hline(COLOR_TEXT_DIM, plot.x + 1, plot.right - 1, base_y)

        points = [to_px(i, v) for i, v in enumerate(history)]
        pygame.draw.aalines(self.screen, COLOR_TEXT, False, points)

        hi_surf = self.font_small.render(f"${hi:,.0f}", False, COLOR_TEXT_DIM)
        lo_surf = self.font_small.render(f"${lo:,.0f}", False, COLOR_TEXT_DIM)
        self.screen.blit(hi_surf, (plot.x + 6, plot.y + 2))
        self.screen.blit(lo_surf, (plot.x + 6, plot.bottom - lo_surf.get_height() - 2))

    def _draw_server_panel(self, servers, start_x, width, mouse_pos, selected_job):
        self._draw_panel_bg(start_x, width)
        self._draw_panel_title("---SERVERPARK---", start_x)

        if selected_job is not None:
            hint = self.font_small.render(
                f"Select a server for: {selected_job.name}", False, COLOR_SELECT)
            self.screen.blit(hint, (start_x + PANEL_PADDING, TAB_BAR_HEIGHT + 65))

        y_offset = TAB_BAR_HEIGHT + 100
        card_width = width - 2 * PANEL_PADDING

        state_colors = {
            ServerState.IDLE: COLOR_IDLE,
            ServerState.WORKING: COLOR_WORKING,
            ServerState.OVERHEATED: COLOR_OVERHEAT
        }

        for server in servers:
            rect = pygame.Rect(start_x + PANEL_PADDING, y_offset, card_width, RACK_HEIGHT)
            self._add_hitbox(rect, "server", server)

            color = state_colors[server.state]

            assignable = selected_job is not None and server.state == ServerState.IDLE
            hovered = rect.collidepoint(mouse_pos)

            bg = COLOR_ROW_HOVER if (assignable and hovered) else COLOR_PANEL_LIGHT
            pygame.draw.rect(self.screen, bg, rect, border_radius=CARD_RADIUS)

            if assignable:
                pygame.draw.rect(self.screen, COLOR_SELECT, rect, 3, border_radius=CARD_RADIUS)
            else:
                pygame.draw.rect(self.screen, color, rect, 2, border_radius=CARD_RADIUS)

            self._draw_server_header(server, rect, color)
            self._draw_temp_bar(server, rect, color)
            self._draw_progress_bar(server, rect)
            self._draw_sell_button(server, rect, mouse_pos)
            self._draw_unload_button(server, rect, mouse_pos)

            y_offset += RACK_HEIGHT + RACK_PADDING

    def _draw_server_header(self, server, rect, color):
        name_text = self.font.render(server.name, False, COLOR_TEXT)
        self.screen.blit(name_text, (rect.x + 15, rect.y + 12))

        status_text = self.font_small.render(server.state.name, False, color)
        status_x = rect.right - status_text.get_width() - 15
        self.screen.blit(status_text, (status_x, rect.y + 18))

        if server.current_job:
            job = server.current_job
            job_text = self.font_small.render(
                f"Job: {job.name}  ({job.remaining_work:,.0f} left)", False, COLOR_TEXT_DIM
            )
            self.screen.blit(job_text, (rect.x + 15, rect.y + 45))

    def _draw_temp_bar(self, server, rect, color):
        label = self.font_small.render("TEMP", False, COLOR_TEXT_DIM)
        self.screen.blit(label, (rect.x + 15, rect.y + 75))

        bar_rect = pygame.Rect(rect.x + 70, rect.y + 78, rect.width - 170, SERVER_BAR_HEIGHT)
        temp_range = server.max_temperature - SERVER_BASE_TEMP
        current = server.temperature - SERVER_BASE_TEMP
        pct = max(0.0, min(1.0, current / temp_range)) if temp_range > 0 else 0.0

        self._draw_bar(bar_rect, pct, color)

        value_text = self.font_small.render(f"{server.temperature:.1f}C", False, color)
        self.screen.blit(value_text, (bar_rect.right + 10, bar_rect.y - 1))

    def _draw_progress_bar(self, server, rect):
        label = self.font_small.render("PROG", False, COLOR_TEXT_DIM)
        self.screen.blit(label, (rect.x + 15, rect.y + 105))

        bar_rect = pygame.Rect(rect.x + 70, rect.y + 108, rect.width - 170, SERVER_BAR_HEIGHT)

        if server.current_job:
            pct = 1.0 - (server.current_job.remaining_work / server.current_job.total_work)
        else:
            pct = 0.0

        self._draw_bar(bar_rect, pct, COLOR_TEXT)

    def _draw_sell_button(self, server, rect, mouse_pos):
        if server.state != ServerState.IDLE:
            return

        btn = pygame.Rect(rect.right - 95, rect.y + 100, SERVER_BTN_WIDTH, SERVER_BTN_HEIGHT)
        self._add_hitbox(btn, "server_sell", server)

        if btn.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn, border_radius=BAR_RADIUS)
        pygame.draw.rect(self.screen, COLOR_OVERHEAT, btn, 1, border_radius=BAR_RADIUS)

        label = self.font_small.render(f"SELL ${server.sell_value():,.0f}", False, COLOR_OVERHEAT)
        self.screen.blit(label, label.get_rect(center=btn.center))

    def _draw_unload_button(self, server, rect, mouse_pos):
        if server.current_job is None:
            return

        btn = pygame.Rect(rect.right - 95, rect.y + 100, SERVER_BTN_WIDTH, SERVER_BTN_HEIGHT)
        self._add_hitbox(btn, "server_unload", server)

        if btn.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn, border_radius=BAR_RADIUS)
        pygame.draw.rect(self.screen, COLOR_WARN, btn, 1, border_radius=BAR_RADIUS)

        label = self.font_small.render("UNLOAD", False, COLOR_WARN)
        self.screen.blit(label, label.get_rect(center=btn.center))

    def _draw_bar(self, rect, pct, fill_color):
        pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=BAR_RADIUS)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 1, border_radius=BAR_RADIUS)

        if pct > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, int(rect.width * pct), rect.height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=BAR_RADIUS)

    def _draw_finance_panel(self, economy, start_x, width, mouse_pos, selected_job):
        self._draw_panel_bg(start_x, width)

        balance_text = self.font.render(f"Balance: ${economy.balance:.2f}", False, COLOR_TEXT)
        self.screen.blit(balance_text, (start_x + PANEL_PADDING, TAB_BAR_HEIGHT + PANEL_PADDING))

        y = TAB_BAR_HEIGHT + 90
        title = self.font.render("--OWNED JOBS--", False, COLOR_TEXT)
        self.screen.blit(title, (start_x + PANEL_PADDING, y))
        y += 45

        if not economy.jobs:
            empty = self.font_small.render("No jobs yet. Buy some!", False, COLOR_TEXT_DIM)
            self.screen.blit(empty, (start_x + PANEL_PADDING, y))
            return

        for job in economy.jobs:
            rect = pygame.Rect(start_x + 10, y, width - 20, OWNED_ROW_HEIGHT - 4)

            running = economy.is_job_running(job)
            selectable = not job.is_decrypted and not running
            sellable = job.is_decrypted

            if selectable:
                self._add_hitbox(rect, "owned_job", job)
            elif sellable:
                self._add_hitbox(rect, "sellable_job", job)

            if job is selected_job:
                pygame.draw.rect(self.screen, COLOR_SELECT, rect, 2, border_radius=BAR_RADIUS)
            elif selectable and rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, COLOR_ROW_HOVER, rect, border_radius=BAR_RADIUS)

            name_color = COLOR_TEXT if (selectable or sellable) else COLOR_TEXT_DIM
            name_surf = self.font_small.render(job.name, False, name_color)
            self.screen.blit(name_surf, (rect.x + 8, rect.y + 6))
            
            if sellable:
                price = economy.market.get_price(job.data_type)
                profit = price - job.cost
                profit_color = COLOR_TEXT if profit >= 0 else COLOR_OVERHEAT
                sign = "+" if profit >= 0 else "-"

                sell_surf = self.font_small.render(f"SELL ${price:,.0f}", False, COLOR_SELECT)
                self.screen.blit(sell_surf, (rect.right - sell_surf.get_width() - 8, rect.y + 6))

                info = f"{job.data_type} | {sign}${abs(profit):,.0f}"
                info_surf = self.font_small.render(info, False, profit_color)
            else:
                status = f"{job.remaining_work:,.0f} left"
                if running:
                    status = "ON SERVER | " + status
                info_surf = self.font_small.render(f"{job.data_type} | {status}", False, COLOR_TEXT_DIM)

            self.screen.blit(info_surf, (rect.x + 8, rect.y + 28))

            y += OWNED_ROW_HEIGHT

    def _draw_game_over(self, economy, mouse_pos):
        self.hitboxes.clear()

        w, h = self.screen.get_size()
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, OVERLAY_ALPHA))
        self.screen.blit(shade, (0, 0))

        box = pygame.Rect(0, 0, GAME_OVER_BOX_WIDTH, GAME_OVER_BOX_HEIGHT)
        box.center = (w // 2, h // 2)
        pygame.draw.rect(self.screen, COLOR_PANEL, box, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_OVERHEAT, box, 3, border_radius=CARD_RADIUS)

        minutes = int(economy.elapsed_time) // 60
        seconds = int(economy.elapsed_time) % 60
        lines = [
            ("--BANKRUPT--", self.font, COLOR_OVERHEAT),
            (economy.game_over_reason, self.font_small, COLOR_TEXT),
            (f"Elapsed time: {minutes}m {seconds:02d}s", self.font, COLOR_TEXT),
            (f"Final balance: ${economy.balance:,.2f}", self.font, COLOR_TEXT),
        ]
        y = box.y + 40
        for text, font, color in lines:
            surf = font.render(text, False, color)
            self.screen.blit(surf, surf.get_rect(midtop=(box.centerx, y)))
            y += surf.get_height() + MENU_BTN_GAP

        btn_restart = pygame.Rect(0, 0, GAME_OVER_BTN_WIDTH, GAME_OVER_BTN_HEIGHT)
        btn_restart.midbottom = (box.centerx - GAME_OVER_BTN_OFFSET_X, box.bottom - 40)
        self._add_hitbox(btn_restart, "restart", None)

        if btn_restart.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn_restart, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_TEXT, btn_restart, 2, border_radius=CARD_RADIUS)
        lbl_restart = self.font.render("RESTART [R]", False, COLOR_TEXT)
        self.screen.blit(lbl_restart, lbl_restart.get_rect(center=btn_restart.center))

        btn_menu = pygame.Rect(0, 0, GAME_OVER_BTN_WIDTH, GAME_OVER_BTN_HEIGHT)
        btn_menu.midbottom = (box.centerx + GAME_OVER_BTN_OFFSET_X, box.bottom - 40)
        self._add_hitbox(btn_menu, "game_over_menu", None)

        if btn_menu.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn_menu, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_TEXT, btn_menu, 2, border_radius=CARD_RADIUS)
        lbl_menu = self.font.render("MAIN MENU [ESC]", False, COLOR_TEXT)
        self.screen.blit(lbl_menu, lbl_menu.get_rect(center=btn_menu.center))

    def _signed_money(self, value, decimals=0):
        sign = "+" if value >= 0 else "-"
        return f"{sign}${abs(value):,.{decimals}f}"

    def _draw_financial(self, economy, mouse_pos, state):
        w = self.screen.get_width()
        self._draw_panel_bg(0, w)
        self._draw_panel_title("---FINANCIAL OVERVIEW---", 0)

        x0 = TABLE_MARGIN
        full_w = w - 2 * TABLE_MARGIN
        y = TAB_BAR_HEIGHT + 80

        cashflow = economy.cashflow_per_minute()
        runway = economy.runway_seconds()
        if runway is None:
            runway_str, runway_color = "NO COSTS", COLOR_TEXT_DIM
        elif runway > RUNWAY_MAX_DISPLAY_SEC:
            runway_str, runway_color = ">1h", COLOR_TEXT
        else:
            runway_str = f"{int(runway) // 60}m {int(runway) % 60:02d}s"
            runway_color = COLOR_OVERHEAT if runway < RUNWAY_WARN_SEC else COLOR_TEXT

        kpis = [
            ("BALANCE", f"${economy.balance:,.0f}",
             COLOR_TEXT if economy.balance >= 0 else COLOR_OVERHEAT),
            ("OPEX / SEC", f"${economy.current_opex_per_sec():,.2f}", COLOR_TEXT),
            (f"NET CASH CHANGE / MIN ({CASHFLOW_WINDOW:.0f}s)", self._signed_money(cashflow),
             COLOR_TEXT if cashflow >= 0 else COLOR_OVERHEAT),
            ("RUNWAY (AT CURRENT OPEX)", runway_str, runway_color),
            ("PROCESSING SERVERS", f"{economy.active_server_count()}/{len(economy.servers)}", COLOR_TEXT),
        ]
        card_w = (full_w - SECTION_GAP * (len(kpis) - 1)) // len(kpis)
        for i, (label, value, color) in enumerate(kpis):
            rect = pygame.Rect(x0 + i * (card_w + SECTION_GAP), y, card_w, KPI_CARD_HEIGHT)
            self._draw_kpi_card(rect, label, value, color)
        y += KPI_CARD_HEIGHT + SECTION_GAP_LARGE

        self._draw_balance_chart(economy.balance_history, pygame.Rect(x0, y, full_w, BALANCE_CHART_HEIGHT))
        y += BALANCE_CHART_HEIGHT + SECTION_GAP_LARGE

        half_w = (full_w - SECTION_GAP) // 2
        self._draw_statement("INCOME STATEMENT (SINCE START)", self._income_rows(economy), x0, y, half_w)
        self._draw_statement("CASH-FLOW STATEMENT (SINCE START)", self._cashflow_rows(economy), x0 + half_w + SECTION_GAP, y, half_w)

    def _draw_kpi_card(self, rect, label, value, color):
        pygame.draw.rect(self.screen, COLOR_PANEL_LIGHT, rect, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 2, border_radius=CARD_RADIUS)
        label_surf = self.font_small.render(label, False, COLOR_TEXT_DIM)
        self.screen.blit(label_surf, (rect.x + 15, rect.y + 12))
        value_surf = self.font.render(value, False, color)
        self.screen.blit(value_surf, (rect.x + 15, rect.y + 48))

    def _draw_balance_chart(self, history, rect):
        pygame.draw.rect(self.screen, COLOR_PANEL_LIGHT, rect, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 2, border_radius=CARD_RADIUS)
        title = self.font_small.render("BALANCE OVER TIME", False, COLOR_TEXT_DIM)
        self.screen.blit(title, (rect.x + 15, rect.y + 10))

        if len(history) < 2:
            return

        plot = pygame.Rect(rect.x + 110, rect.y + 40, rect.width - 130, rect.height - 60)
        pygame.draw.rect(self.screen, COLOR_BORDER, plot, 1)

        times = [t for t, _ in history]
        values = [v for _, v in history]
        t0, t1 = times[0], times[-1]
        t_span = max(t1 - t0, 0.001)
        v_min, v_max = min(values), max(values)
        if v_max == v_min:
            v_max += 100
            v_min -= 100
        pad = (v_max - v_min) * BALANCE_CHART_PAD_RATIO
        v_min -= pad
        v_max += pad

        def to_px(t, v):
            px = plot.x + (t - t0) / t_span * plot.width
            py = plot.bottom - (v - v_min) / (v_max - v_min) * plot.height
            return (px, py)

        if v_min < 0 < v_max:
            _, zero_y = to_px(t0, 0)
            pygame.draw.line(self.screen, COLOR_OVERHEAT, (plot.x, zero_y), (plot.right, zero_y), 1)

        points = [to_px(t, v) for t, v in history]
        pygame.draw.aalines(self.screen, COLOR_TEXT, False, points)

        max_lbl = self.font_small.render(f"${v_max:,.0f}", False, COLOR_TEXT_DIM)
        min_lbl = self.font_small.render(f"${v_min:,.0f}", False, COLOR_TEXT_DIM)
        self.screen.blit(max_lbl, (rect.x + 15, plot.y - 6))
        self.screen.blit(min_lbl, (rect.x + 15, plot.bottom - 12))
        span_lbl = self.font_small.render(f"last {int(t_span)}s", False, COLOR_TEXT_DIM)
        self.screen.blit(span_lbl, (rect.right - span_lbl.get_width() - 15, rect.y + 10))

    def _income_rows(self, economy):
        s = economy.income_statement()
        p = economy.asset_position()
        margin = "N/A" if s["operating_margin"] is None else f"{s['operating_margin']:.1f}%"
        return [
            ("Revenue (job sales)", s["revenue"], "item"),
            ("Cost of jobs sold", -s["cogs"], "item"),
            ("Gross profit", s["gross_profit"], "total"),
            ("Operating expenses (OPEX)", -s["opex"], "item"),
            ("Depreciation (servers)", -s["depreciation"], "item"),
            ("Operating result", s["operating_result"], "total"),
            ("Result on server disposal", s["disposal_result"], "item"),
            ("Net result", s["net_result"], "total"),
            (f"Operating margin: {margin}", None, "header"),
            ("Unsold jobs held (at cost)", p["inventory_at_cost"], "note"),
            ("Servers (book value)", p["servers_at_book"], "note"),
        ]

    def _cashflow_rows(self, economy):
        c = economy.cashflow_statement()
        return [
            ("OPERATING ACTIVITIES", None, "header"),
            ("Job sales", c["job_sales"], "item"),
            ("Job purchases", -c["job_purchases"], "item"),
            ("OPEX paid", -c["opex"], "item"),
            ("Operating cash-flow", c["operating"], "total"),
            ("INVESTING ACTIVITIES", None, "header"),
            ("Server sales", c["server_sales"], "item"),
            ("Server purchases", -c["server_purchases"], "item"),
            ("Investing cash-flow", c["investing"], "total"),
            ("Net cash change", c["net_change"], "total"),
        ]

    def _draw_statement(self, title, rows, x, y, w):
        title_surf = self.font.render(title, False, COLOR_TEXT)
        self.screen.blit(title_surf, (x, y))
        y += 45
        pygame.draw.line(self.screen, COLOR_BORDER, (x, y), (x + w, y), 2)
        y += 8

        for label, value, style in rows:
            if style == "total":
                pygame.draw.line(self.screen, COLOR_BORDER, (x, y), (x + w, y), 1)
                y += 4
            label_color = COLOR_TEXT if style == "total" else COLOR_TEXT_DIM
            label_surf = self.font.render(label, False, label_color)
            self.screen.blit(label_surf, (x + 10, y))

            if value is not None:
                if style == "note":
                    text, color = f"${value:,.0f}", COLOR_TEXT_DIM
                else:
                    text = self._signed_money(value, decimals=2)
                    color = COLOR_TEXT if value >= 0 else COLOR_OVERHEAT
                value_surf = self.font.render(text, False, color)
                self.screen.blit(value_surf, (x + w - value_surf.get_width() - 10, y))
            y += STATEMENT_ROW_HEIGHT