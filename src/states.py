class BaseState:
    label = "UNNAMED"

    def draw(self, view, economy, mouse_pos):
        raise NotImplementedError("draw method must be implemented in subclasses")

    def handle_click(self, pos, economy):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

class DashboardState(BaseState):
    label = "Dashboard"

    def draw(self, view, economy, mouse_pos):
        market_w = int(view.screen.get_width() * 0.3)
        server_w = int(view.screen.get_width() * 0.5)
        finance_w = int(view.screen.get_width() * 0.2)

        view._draw_market_panel(economy.market, 0, market_w)
        view._draw_server_panel(economy.servers, market_w, server_w)
        view._draw_finance_panel(economy, market_w + server_w, finance_w)