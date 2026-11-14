from model import ServerState

class BaseState:
    label = "UNNAMED"

    def handle_click(self, hit, economy):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

class DashboardState(BaseState):
    label = "[F1] Dashboard"

    def __init__(self):
        self.selected_job = None

    def handle_click(self, hit, economy):
        if hit is None:
            self.selected_job = None
            return
        kind, obj = hit

        if kind == "owned_job":
            self.selected_job = None if obj is self.selected_job else obj
        elif kind == "sellable_job":
            economy.sell_job(obj)
        elif kind == "server" and self.selected_job is not None:
            if obj.state == ServerState.IDLE:
                server_index = economy.servers.index(obj)
                economy.assign_job_to_server(server_index, self.selected_job)
                self.selected_job = None
        elif kind == "server_sell":
            economy.sell_server(obj)
        elif kind == "server_unload":
            economy.unload_server(obj)
        
    def on_exit(self):
        self.selected_job = None

class MarketplaceState(BaseState):
    label = "[F2] Marketplace"

    def __init__(self):
        self.last_purchased_model = None

    def handle_click(self, hit, economy):
        if hit is None:
            return
        kind, obj = hit
        if kind == "job":
            economy.buy_job(obj)
        elif kind == "server_offer":
            old_server_count = len(economy.servers)
            economy.buy_server(obj)
            if len(economy.servers) > old_server_count:
                self.last_purchased_model = obj["model"]

class FinancialState(BaseState):
    label = "[F3] Financial"