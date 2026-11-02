class BaseState:
    label = "UNNAMED"

    def handle_click(self, hit, economy):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

class DashboardState(BaseState):
    label = "Dashboard"

class MarketplaceState(BaseState):
    label = "Marketplace"

    def handle_click(self, hit, economy):
        if hit is None:
            return
        kind, obj = hit
        if kind == "job":
            economy.buy_job(obj)