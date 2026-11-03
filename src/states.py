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
    label = "Dashboard"

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
        
    def on_exit(self):
        self.selected_job = None

class MarketplaceState(BaseState):
    label = "Marketplace"

    def handle_click(self, hit, economy):
        if hit is None:
            return
        kind, obj = hit
        if kind == "job":
            economy.buy_job(obj)
        elif kind == "server_offer":
            economy.buy_server(obj)