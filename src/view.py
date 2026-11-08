import pygame
from settings import *
from model import ServerState

class GameView:
    JOB_COLUMNS = [
        ("NAME",     0.00, "left"),
        ("CATEGORY", 0.28, "left"),
        ("WORK",     0.50, "right"),
        ("COST",     0.64, "right"),
        ("PROFIT",   0.82, "right"),
        ("EXPIRES",  0.97, "right"),
    ]
    SHOP_COLUMNS = [
        ("MODEL",    0.00, "left"),
        ("SPEED",    0.45, "right"),
        ("MAX TEMP", 0.58, "right"),
        ("OPEX",     0.70, "right"),
        ("COST",     0.85, "right"),
    ]
    
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

    def draw(self, economy, states, active_tab_key, mouse_pos):
        self.screen.fill(COLOR_BG)
        self.hitboxes.clear()

        tabs = {key: state.label for key, state in states.items()}
        self._draw_tab_bar(tabs, active_tab_key)

        self.renderers[active_tab_key](economy, mouse_pos, states[active_tab_key])

        if economy.game_over:
            self._draw_game_over(economy, mouse_pos)
            
        pygame.display.flip()

    def _add_hitbox(self, rect, kind, obj):
        self.hitboxes.append({"rect": rect, "kind": kind, "obj": obj})

    def get_hit(self, pos):
        for hb in reversed(self.hitboxes):
            if hb["rect"].collidepoint(pos):
                return (hb["kind"], hb["obj"])
        return None

    def _draw_dashboard(self, economy, mouse_pos, state):
        w = self.screen.get_width()
        market_w = int(w * 0.3)
        server_w = int(w * 0.5)
        finance_w = int(w * 0.2)

        self._draw_market_panel(economy.market, 0, market_w)
        self._draw_server_panel(economy.servers, market_w, server_w, mouse_pos, state.selected_job)
        self._draw_finance_panel(economy, market_w + server_w, finance_w, mouse_pos, state.selected_job)

    def _draw_marketplace(self, economy, mouse_pos, state):
        panel_w = self.screen.get_width()
        self._draw_panel_bg(0, panel_w)
        self._draw_panel_title("---JOB MARKET---", 0)

        count_str = f"{len(economy.job_market)}/{economy.job_generator.pool_max_size}"
        count_surf = self.font.render(count_str, False, COLOR_TEXT_DIM)
        self.screen.blit(count_surf, (panel_w - TABLE_MARGIN - count_surf.get_width(),
                                      TAB_BAR_HEIGHT + 20))

        table_x = TABLE_MARGIN
        table_w = panel_w - 2 * TABLE_MARGIN
        y = TAB_BAR_HEIGHT + 90

        for text, frac, align in self.JOB_COLUMNS:
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
                     COLOR_OVERHEAT if job.time_left < 10 else COLOR_TEXT_DIM),
                ]
                for (_, frac, align), (value, color) in zip(self.JOB_COLUMNS, values):
                    self._blit_cell(self.font, value, color,
                                    table_x + 10, table_w - 20, frac, align, y + 8)

                pygame.draw.line(self.screen, COLOR_BORDER,
                                 (table_x, row_rect.bottom), (table_x + table_w, row_rect.bottom), 1)
                y += ROW_HEIGHT
        y += 30
        self._draw_server_shop(economy, mouse_pos, table_x, table_w, y)

    def _draw_server_shop(self, economy, mouse_pos, table_x, table_w, y):
        title = self.font.render("---SERVER SHOP---", False, COLOR_TEXT)
        self.screen.blit(title, (table_x, y))

        count_surf = self.font.render(f"{len(economy.servers)}/{MAX_SERVERS}", False, COLOR_TEXT_DIM)
        self.screen.blit(count_surf, (table_x + table_w - count_surf.get_width(), y))
        y += 50

        for text, frac, align in self.SHOP_COLUMNS:
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
                (f"{offer['processing_speed']:g}", text_color),
                (f"{offer['max_temperature']:g}C", text_color),
                (f"${offer['opex']:,.0f}/s", text_color),
                (f"${offer['capex']:,.0f}", cost_color),
            ]
            for (_, frac, align), (value, color) in zip(self.SHOP_COLUMNS, values):
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
        x = 20

        for key, label in tabs.items():
            is_active = (key == active_tab_key)
            color = COLOR_TEXT if is_active else COLOR_TEXT_DIM

            text_surface = self.font.render(label, False, color)
            text_rect = text_surface.get_rect(topleft=(x, 12))
            self.screen.blit(text_surface, text_rect)

            self.tab_rects[key] = text_rect

            x += text_rect.width + 40

    def _draw_panel_bg(self, start_x, width):
        panel_rect = pygame.Rect(start_x, TAB_BAR_HEIGHT, width, SCREEN_HEIGHT - TAB_BAR_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, panel_rect, 2)

    def _draw_panel_title(self, text, start_x):
        title_text = self.font.render(text, False, COLOR_TEXT)
        self.screen.blit(title_text, (start_x + 20, TAB_BAR_HEIGHT + 20))

    def _draw_market_panel(self, market, start_x, width):
        self._draw_panel_bg(start_x, width)
        self._draw_panel_title("---BLACKMARKET---", start_x)
        
        y_offset = TAB_BAR_HEIGHT + 100

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

    def _draw_server_panel(self, servers, start_x, width, mouse_pos, selected_job):
        self._draw_panel_bg(start_x, width)
        self._draw_panel_title("---SERVERPARK---", start_x)

        if selected_job is not None:
            hint = self.font_small.render(
                f"Select a server for: {selected_job.name}", False, COLOR_SELECT)
            self.screen.blit(hint, (start_x + 20, TAB_BAR_HEIGHT + 65))

        y_offset = TAB_BAR_HEIGHT + 100
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

            y_offset += rack_height + rack_padding

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

        if server.current_job:
            pct = 1.0 - (server.current_job.remaining_work / server.current_job.total_work)
        else:
            pct = 0.0

        self._draw_bar(bar_rect, pct, COLOR_TEXT)

    def _draw_sell_button(self, server, rect, mouse_pos):
        if server.state != ServerState.IDLE:
            return

        btn = pygame.Rect(rect.right - 95, rect.y + 100, 85, 30)
        self._add_hitbox(btn, "server_sell", server)

        if btn.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_OVERHEAT, btn, 1, border_radius=4)

        label = self.font_small.render(f"SELL ${server.sell_value():,.0f}", False, COLOR_OVERHEAT)
        self.screen.blit(label, label.get_rect(center=btn.center))

    def _draw_unload_button(self, server, rect, mouse_pos):
        if server.current_job is None:
            return

        btn = pygame.Rect(rect.right - 95, rect.y + 100, 85, 30)
        self._add_hitbox(btn, "server_unload", server)

        if btn.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_WARN, btn, 1, border_radius=4)

        label = self.font_small.render("UNLOAD", False, COLOR_WARN)
        self.screen.blit(label, label.get_rect(center=btn.center))

    def _draw_bar(self, rect, pct, fill_color):
        pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 1, border_radius=4)

        if pct > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, int(rect.width * pct), rect.height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=4)

    def _draw_finance_panel(self, economy, start_x, width, mouse_pos, selected_job):
        self._draw_panel_bg(start_x, width)

        # title
        balance_text = self.font.render(f"Balance: ${economy.balance:.2f}", False, COLOR_TEXT)
        self.screen.blit(balance_text, (start_x + 20, TAB_BAR_HEIGHT + 20))

        y = TAB_BAR_HEIGHT + 90
        title = self.font.render("--OWNED JOBS--", False, COLOR_TEXT)
        self.screen.blit(title, (start_x + 20, y))
        y += 45

        if not economy.jobs:
            empty = self.font_small.render("No jobs yet. Buy some!", False, COLOR_TEXT_DIM)
            self.screen.blit(empty, (start_x + 20, y))
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
                pygame.draw.rect(self.screen, COLOR_SELECT, rect, 2, border_radius=4)
            elif selectable and rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, COLOR_ROW_HOVER, rect, border_radius=4)

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
        shade.fill((0, 0, 0, 200))
        self.screen.blit(shade, (0, 0))

        box = pygame.Rect(0, 0, 800, 420)
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
            y += surf.get_height() + 25

        btn = pygame.Rect(0, 0, 300, 60)
        btn.midbottom = (box.centerx, box.bottom - 40)
        self._add_hitbox(btn, "restart", None)

        if btn.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_ROW_HOVER, btn, border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, COLOR_TEXT, btn, 2, border_radius=CARD_RADIUS)

        label = self.font.render("RESTART [R]", False, COLOR_TEXT)
        self.screen.blit(label, label.get_rect(center=btn.center))

    def _signed_money(self, value):
        sign = "+" if value >= 0 else "-"
        return f"{sign}${abs(value):,.0f}"

    def _draw_financial(self, economy, mouse_pos, state):
        w = self.screen.get_width()
        self._draw_panel_bg(0, w)
        self._draw_panel_title("---FINANCIAL OVERVIEW---", 0)

        x0 = TABLE_MARGIN
        full_w = w - 2 * TABLE_MARGIN
        gap = 20
        y = TAB_BAR_HEIGHT + 80

        cashflow = economy.cashflow_per_minute()
        runway = economy.runway_seconds()
        if runway is None:
            runway_str, runway_color = "NO COSTS", COLOR_TEXT_DIM
        elif runway > 3600:
            runway_str, runway_color = ">1h", COLOR_TEXT
        else:
            runway_str = f"{int(runway) // 60}m {int(runway) % 60:02d}s"
            runway_color = COLOR_OVERHEAT if runway < 60 else COLOR_TEXT

        kpis = [
            ("BALANCE", f"${economy.balance:,.0f}",
             COLOR_TEXT if economy.balance >= 0 else COLOR_OVERHEAT),
            ("OPEX / SEC", f"${economy.current_opex_per_sec():,.2f}", COLOR_TEXT),
            ("CASH-FLOW / MIN", self._signed_money(cashflow),
             COLOR_TEXT if cashflow >= 0 else COLOR_OVERHEAT),
            ("RUNWAY", runway_str, runway_color),
            ("ACTIVE SERVERS", f"{economy.active_server_count()}/{len(economy.servers)}", COLOR_TEXT),
        ]
        card_w = (full_w - gap * (len(kpis) - 1)) // len(kpis)
        card_h = 100
        for i, (label, value, color) in enumerate(kpis):
            rect = pygame.Rect(x0 + i * (card_w + gap), y, card_w, card_h)
            self._draw_kpi_card(rect, label, value, color)
        y += card_h + 30

        chart_h = 280
        self._draw_balance_chart(economy.balance_history, pygame.Rect(x0, y, full_w, chart_h))
        y += chart_h + 30

        half_w = (full_w - gap) // 2
        self._draw_statement("INCOME STATEMENT", self._income_rows(economy), x0, y, half_w)
        self._draw_statement("CASH-FLOW STATEMENT", self._cashflow_rows(economy),
                             x0 + half_w + gap, y, half_w)

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
        pad = (v_max - v_min) * 0.1
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
        t = economy.totals
        gross = t["job_sales"] - t["job_purchases"]
        result = gross - t["opex"]
        margin = result / t["job_sales"] * 100.0 if t["job_sales"] > 0 else 0.0
        return [
            ("Job sales revenue", t["job_sales"], "item"),
            ("Cost of jobs purchased", -t["job_purchases"], "item"),
            ("Gross margin", gross, "total"),
            ("Operating expenses (OPEX)", -t["opex"], "item"),
            ("Operating result", result, "total"),
            (f"Operating margin: {margin:.0f}%", None, "header"),
        ]

    def _cashflow_rows(self, economy):
        t = economy.totals
        operating = t["job_sales"] - t["job_purchases"] - t["opex"]
        investing = t["server_sales"] - t["server_purchases"]
        return [
            ("OPERATING ACTIVITIES", None, "header"),
            ("Job sales", t["job_sales"], "item"),
            ("Job purchases", -t["job_purchases"], "item"),
            ("OPEX paid", -t["opex"], "item"),
            ("Operating cash-flow", operating, "total"),
            ("INVESTING ACTIVITIES", None, "header"),
            ("Server sales", t["server_sales"], "item"),
            ("Server purchases", -t["server_purchases"], "item"),
            ("Investing cash-flow", investing, "total"),
            ("Net cash change", operating + investing, "total"),
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
                value_color = COLOR_TEXT if value >= 0 else COLOR_OVERHEAT
                value_surf = self.font.render(self._signed_money(value), False, value_color)
                self.screen.blit(value_surf, (x + w - value_surf.get_width() - 10, y))
            y += 34