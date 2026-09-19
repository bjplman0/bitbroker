class Server:
    def __init__(self, name, capex, opex, processing_speed):
        self.name = name
        self.capex = capex
        self.opex_per_sec = opex
        self.processing_speed = processing_speed

        self.is_active = False
        self.temperature = 30.0
        self.max_temperature = 95.0
        self.current_job= None

    def update(self, dt):
        if self.is_active:
            self.temperature += 0.1 * dt
            if self.temperature > self.max_temperature:
                self.is_active = False
                print(f"{self.name} has overheated and is temporarily paused.")
        else:
            if self.temperature > 30.0:
                self.temperature -= 0.2 * dt
                if self.temperature < 30.0:
                    self.temperature = 30.0


class EconomyModel:
    def __init__(self, starting_balance):
        self.balance = starting_balance
        self.servers = []

    def add_server(self, server):
        self.servers.append(server)

    def update(self, dt):
        total_opex = 0.0
        for server in self.servers:
            server.update(dt)
            if server.is_active:
                total_opex += server.opex_per_sec * dt
            else:
                total_opex += (server.opex_per_sec * 0.2) * dt
        self.balance -= total_opex