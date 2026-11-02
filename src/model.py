from settings import (
    SERVER_BASE_TEMP,
    SERVER_HEATING_RATE,
    SERVER_COOLING_RATE,
    MARKET_TICK_RATE,
    MARKET_CATEGORIES_CONFIG,
    MARKET_HISTORY_LENGTH,
    JOB_GENERATION_INTERVAL,
    JOB_POOL_MAX_SIZE,
    JOB_WORK_VARIANCE,
    JOB_COST_RATIO
)
from name_generator import generate_name
import random
from enum import Enum

class Job:
    def __init__(self, name, total_work, data_type, cost = 0.0):
        self.name = name
        self.total_work = total_work
        self.remaining_work = total_work
        self.data_type = data_type
        self.cost = cost
        self.is_decrypted = False

class JobGenerator:
    def __init__(self, market):
        self.market = market
        self.time_since_last_spawn = 0.0
        self.spawn_interval = JOB_GENERATION_INTERVAL
        self.pool_max_size = JOB_POOL_MAX_SIZE

    def update(self, dt, current_pool_size):
        self.time_since_last_spawn += dt

        if self.time_since_last_spawn > self.spawn_interval:
            self.time_since_last_spawn = 0.0
            if current_pool_size < self.pool_max_size:
                return self._generate_job()

        return None

    def _generate_job(self):
        category_name = random.choice(list(self.market.categories.keys()))
        category = self.market.categories[category_name]
        config = MARKET_CATEGORIES_CONFIG[category_name]

        variance = random.uniform(1.0 - JOB_WORK_VARIANCE, 1.0 + JOB_WORK_VARIANCE)
        total_work = round(config["job_work_base"] * variance, 1)
        cost = round(category.current_price * JOB_COST_RATIO, 2)

        name = generate_name(category_name)

        return Job(name=name, total_work=total_work, data_type=category_name, cost=cost)

class ServerState(Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    OVERHEATED = "OVERHEATED"

class Server:
    def __init__(self, name, capex, opex, processing_speed, max_temperature, idle_multiplier):
        self.name = name
        self.capex = capex
        self.opex_per_sec = opex
        self.processing_speed = processing_speed
        self.max_temperature = max_temperature
        self.idle_multiplier = idle_multiplier

        self.state = ServerState.IDLE
        self.temperature = SERVER_BASE_TEMP
        self.current_job = None

    def start_job(self, job):
        if self.state != ServerState.IDLE:
            print(f"[{self.name}] cannot start job. Server is currently {self.state.name}.")
            return
        if job.is_decrypted:
            print(f"[{self.name}] cannot start job: {job.name} is already decrypted.")
            return
        
        self.current_job = job
        self.state = ServerState.WORKING
        print(f"[{self.name}] is now working on: {self.current_job.name}")
        
    def update(self, dt):
        finished_job = None

        if self.state == ServerState.WORKING:
            self.temperature += SERVER_HEATING_RATE * dt
            self.current_job.remaining_work -= self.processing_speed * dt
            if self.current_job.remaining_work <= 0:
                self.current_job.remaining_work = 0
                self.current_job.is_decrypted = True
                finished_job = self.current_job
                self.current_job = None
                self.state = ServerState.IDLE
            elif self.temperature > self.max_temperature:
                self.state = ServerState.OVERHEATED

        elif self.state == ServerState.OVERHEATED:
            self.temperature -= SERVER_COOLING_RATE * dt
            if self.temperature < SERVER_BASE_TEMP:
                self.temperature = SERVER_BASE_TEMP
                if self.current_job is not None:
                    self.state = ServerState.WORKING
                else:
                    self.state = ServerState.IDLE

        elif self.state == ServerState.IDLE:
            if self.temperature > SERVER_BASE_TEMP:
                self.temperature -= SERVER_COOLING_RATE * dt
                if self.temperature < SERVER_BASE_TEMP:
                    self.temperature = SERVER_BASE_TEMP

        return finished_job

class DataCategory:
    def __init__(self, name, base_price, volatility, gravity, min_price, max_price):
        self.name = name
        self.base_price = base_price
        self.current_price = base_price
        self.volatility = volatility
        self.gravity = gravity
        self.min_price = min_price
        self.max_price = max_price
        self.history_length = MARKET_HISTORY_LENGTH
        self.price_history = [base_price] * self.history_length

    def update_price(self):
        fluctuation = random.uniform(-self.volatility, self.volatility) * self.base_price
        distance = self.base_price - self.current_price
        pull = distance * self.gravity
        self.current_price += fluctuation + pull

        self.current_price = max(self.min_price, min(self.current_price, self.max_price))

        self.price_history.append(self.current_price)
        if len(self.price_history) > self.history_length:
            self.price_history.pop(0)

class Market:
    def __init__(self):
        self.categories = {}
        for name, data in MARKET_CATEGORIES_CONFIG.items():
            self.categories[name] = DataCategory(
                name = name,
                base_price = data["base_price"],
                volatility = data["volatility"],
                gravity = data["gravity"],
                min_price = data["min_price"],
                max_price = data["max_price"]
            )

        self.time_since_last_tick = 0.0
        self.tick_rate = MARKET_TICK_RATE

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
        self.job_market = []
        self.job_generator = JobGenerator(self.market)

    def add_server(self, server):
        self.servers.append(server)

    def add_job(self, job):
        self.jobs.append(job)

    def buy_job(self, job):
        if job not in self.job_market:
            print(f"Cannot buy job: {job.name} is not available in the job market.")
            return
        if self.balance < job.cost:
            print(f"Cannot buy job: {job.name}. Insufficient balance (needs ${job.cost:.2f}).")
            return

        self.balance -= job.cost
        self.job_market.remove(job)
        self.add_job(job)
        print(f"Bought job: {job.name} for ${job.cost:.2f}. New balance: ${self.balance:.2f}")

    def assign_job_to_server(self, server_index, job):
        if job not in self.jobs:
            print("Job not found in the job list.")
            return
        if self.is_job_running(job):
            print(f"Job {job.name} is already running on a server.")
            return
        
        server = self.servers[server_index]
        server.start_job(job)

    def is_job_running(self, job):
        return any(server.current_job is job for server in self.servers)

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

        new_job = self.job_generator.update(dt, len(self.job_market))
        if new_job is not None:
            self.job_market.append(new_job)

            # print(f"New job available: {new_job.name} ({new_job.data_type}, cost: ${new_job.cost:.2f}, work: {new_job.total_work})")

        total_opex = 0.0

        for server in self.servers:
            finished_job = server.update(dt)
            if finished_job is not None:
                pass
            if server.state in [ServerState.WORKING, ServerState.OVERHEATED]:
                total_opex += server.opex_per_sec * dt
            else:
                total_opex += (server.opex_per_sec * server.idle_multiplier) * dt

        self.balance -= total_opex

        