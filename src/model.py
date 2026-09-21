class Job:
    def __init__(self, name, total_work, data_type):
        self.name = name
        self.total_work = total_work
        self.remaining_work = total_work
        self.data_type = data_type
        self.is_decrypted = False

class Server:
    def __init__(self, name, capex, opex, processing_speed, max_temperature, idle_multiplier):
        self.name = name
        self.capex = capex
        self.opex_per_sec = opex
        self.processing_speed = processing_speed
        self.max_temperature = max_temperature
        self.idle_multiplier = idle_multiplier

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

import random

class DataCategory:
    def __init__(self, name, base_price, volatility, gravity):
        self.name = name
        self.base_price = base_price
        self.current_price = base_price
        self.volatility = volatility
        self.gravity = gravity

    def update_price(self):
        fluctuation = random.uniform(-self.volatility, self.volatility) * self.base_price
        distance = self.base_price - self.current_price
        pull = distance * self.gravity
        self.current_price += fluctuation + pull

        if self.current_price < 0:
            self.current_price = 0

class Market:
    def __init__(self):
        self.categories = {
            "Personal": DataCategory("Personal", 100.0, 0.1, 0.05),
            "Small Business": DataCategory("Small Business", 1000.0, 0.2, 0.1),
            "Large Corporation": DataCategory("Large Corporation", 10000.0, 0.3, 0.2),
            "Government": DataCategory("Government", 10000.0, 0.3, 0.2),
            "Military": DataCategory("Military", 100000.0, 0.4, 0.3),
        }
        self.time_since_last_tick = 0.0
        self.tick_rate = 1.0

    def update(self, dt):
        self.time_since_last_tick += dt

        if self.time_since_last_tick > self.tick_rate:
            self.time_since_last_tick = 0.0
            for category in self.categories.values():
                category.update_price()

    def get_price(self, data_type):
        if data_type in self.categories:
            return self.categories[data_type].current_price
        return 0.0
    
class EconomyModel:
    def __init__(self, starting_balance):
        self.balance = starting_balance
        self.servers = []
        self.jobs = []
        self.market = Market()

    def add_server(self, server):
        self.servers.append(server)

    def add_job(self, job):
        self.jobs.append(job)

    def sell_job(self, job):
        if job in self.jobs and job.is_decrypted:
            price = self.market.get_price(job.data_type)
            self.balance += price
            self.jobs.remove(job)
            print(f"Sold job: {job.name} for ${price:.2f}. New balance: ${self.balance:.2f}")
        else:
            print(f"Cannot sell job: {job.name}. It is either not in the job list or not decrypted.")

    def update(self, dt):
        self.market.update(dt)

        total_opex = 0.0

        for server in self.servers:
            finished_job = server.update(dt)
            if finished_job is not None:
                pass
            if server.is_active:
                total_opex += server.opex_per_sec * dt
            else:
                total_opex += (server.opex_per_sec * server.idle_multiplier) * dt

        self.balance -= total_opex

        