class Job:
    def __init__(self, name, total_work, data_type):
        self.name = name
        self.total_work = total_work
        self.remaining_work = total_work
        self.data_type = data_type
        self.is_decrypted = False

class Server:
    def __init__(self, name, capex, opex, processing_speed, max_temperature):
        self.name = name
        self.capex = capex
        self.opex_per_sec = opex
        self.processing_speed = processing_speed
        self.max_temperature = max_temperature

        self.is_active = False
        self.temperature = 30.0
        self.current_job= None

    def start_job(self, job):
        if self.is_active or self.current_job is not None:
            print(f"[{self.name}] is already working on a job. Cannot start a new job.")
            return
        self.current_job = job
        self.is_active = True
        print(f"[{self.name}] is working on: {self.current_job.name}")
        
    def update(self, dt):
        finished_job = None

        if self.is_active and self.current_job is not None:
            self.temperature += 0.1 * dt
            self.current_job.remaining_work -= self.processing_speed * dt

            if self.current_job.remaining_work <= 0:
                self.current_job.remaining_work = 0
                self.current_job.is_decrypted = True
                finished_job = self.current_job
                self.is_active = False
                self.current_job = None
                print(f"[{self.name}] finished job: {finished_job.name}")
            elif self.temperature > self.max_temperature:
                self.is_active = False
                print(f"[{self.name}] has overheated and is temporarily paused.")
        else:
            if self.temperature > 30.0:
                self.temperature -= 0.2 * dt
                if self.temperature < 30.0:
                    self.temperature = 30.0

        return finished_job

class EconomyModel:
    def __init__(self, starting_balance):
        self.balance = starting_balance
        self.servers = []
        self.jobs = []

    def add_server(self, server):
        self.servers.append(server)

    def add_job(self, job):
        self.jobs.append(job)

    def update(self, dt):
        total_opex = 0.0

        for server in self.servers:
            finished_job = server.update(dt)
            if finished_job is not None:
                pass
            if server.is_active:
                total_opex += server.opex_per_sec * dt
            else:
                total_opex += (server.opex_per_sec * 0.2) * dt
                #ide meg a 0.2-vel kezdeni kell valamit

        self.balance -= total_opex

        