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