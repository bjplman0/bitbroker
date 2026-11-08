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
    MAX_SERVERS,
    SERVER_RESALE_RATIO,
    SERVER_LIFETIME,
    SERVER_SALVAGE_RATIO,
    JOB_COST_RATIO_MIN,
    JOB_COST_RATIO_MAX,
    JOB_LIFETIME_MIN,
    JOB_LIFETIME_MAX,
    SERVER_CATALOG,
    BALANCE_SAMPLE_INTERVAL,
    BALANCE_HISTORY_LENGTH,
    LEDGER_MAX_ENTRIES
)
from name_generator import generate_name
import random
from enum import Enum
from collections import deque

class Job:
    def __init__(self, name, total_work, data_type, cost = 0.0, lifetime = 0.0):
        self.name = name
        self.total_work = total_work
        self.remaining_work = total_work
        self.data_type = data_type
        self.cost = cost
        self.is_decrypted = False
        self.time_left = lifetime

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

        cost_ratio = random.uniform(JOB_COST_RATIO_MIN, JOB_COST_RATIO_MAX)
        cost = round(category.current_price * cost_ratio, 2)

        lifetime = random.uniform(JOB_LIFETIME_MIN, JOB_LIFETIME_MAX)
        name = generate_name(category_name)

        return Job(name=name, total_work=total_work, data_type=category_name, cost=cost, lifetime=lifetime)

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
        self.age = 0.0

    def start_job(self, job):
        if self.state != ServerState.IDLE:
            print(f"[{self.name}] cannot start job. Server is currently {self.state.name}.")
            return
        if job.is_decrypted:
            print(f"[{self.name}] cannot start job: {job.name} is already decrypted.")
            return
        
        self.current_job = job
        self.state = ServerState.WORKING

    def unload_job(self):
        job = self.current_job
        self.current_job = None

        if self.state != ServerState.OVERHEATED:
            self.state = ServerState.IDLE

        return job

    def book_value(self):
        salvage = self.capex * SERVER_SALVAGE_RATIO
        used = min(self.age / SERVER_LIFETIME, 1.0)
        return self.capex - (self.capex - salvage) * used

    def depreciate(self, dt):
        salvage = self.capex * SERVER_SALVAGE_RATIO
        remaining = max(SERVER_LIFETIME - self.age, 0.0)
        step = min(dt, remaining)
        self.age += dt
        return (self.capex - salvage) / SERVER_LIFETIME * step

    def sell_value(self):
        return self.book_value() * SERVER_RESALE_RATIO
    
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
        self._next_server_id = 1
        self.game_over = False
        self.game_over_reason = ""
        self.elapsed_time = 0.0
        self.ledger = deque(maxlen=LEDGER_MAX_ENTRIES)
        self.starting_balance = starting_balance
        self.totals = {
            "job_sales": 0.0, "job_purchases": 0.0, 
            "server_sales": 0.0, "server_purchases": 0.0, 
            "opex": 0.0,
            "cogs": 0.0,
            "depreciation": 0.0,
            "server_disposal_result": 0.0,
        }
        self.balance_history = deque(maxlen=BALANCE_HISTORY_LENGTH)
        self.balance_history.append((0.0, starting_balance))
        self._time_since_sample = 0.0

    def add_server(self, server):
        self.servers.append(server)
        self._next_server_id += 1

    def buy_server(self, template):
        if len(self.servers) >= MAX_SERVERS:
            print(f"Cannot buy server: Maximum number of servers ({MAX_SERVERS}) reached.")
            return
        if self.balance < template["capex"]:
            print(f"Cannot buy server: Insufficient balance (needs ${template['capex']:.2f}).")
            return

        self.balance -= template["capex"]
        self._record("server_purchases", -template["capex"], template["model"])
        server = Server(
            name = f"Server-{self._next_server_id:02d}",
            capex = template["capex"],
            opex = template["opex"],
            processing_speed = template["processing_speed"],
            max_temperature = template["max_temperature"],
            idle_multiplier = template["idle_multiplier"]
        )
        self.add_server(server)

    def sell_server(self, server):
        if server not in self.servers:
            print("Cannot sell server: not owned.")
            return
        
        if server.state != ServerState.IDLE or server.current_job is not None:
            print(f"Cannot sell {server.name}: it is busy.")
            return

        value = server.sell_value()
        self.balance += value
        self._record("server_sales", value, server.name)
        self.totals["server_disposal_result"] += value - server.book_value()
        self.servers.remove(server)
        
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
        self._record("job_purchases", -job.cost, job.name)
        self.job_market.remove(job)
        self.add_job(job)

    def assign_job_to_server(self, server_index, job):
        if job not in self.jobs:
            print("Job not found in the job list.")
            return
        if self.is_job_running(job):
            print(f"Job {job.name} is already running on a server.")
            return
        
        server = self.servers[server_index]
        server.start_job(job)

    def unload_server(self, server):
        if server not in self.servers or server.current_job is None:
            print("Nothing to unload.")
            return
        job = server.unload_job()

    def is_job_running(self, job):
        return any(server.current_job is job for server in self.servers)

    def sell_job(self, job):
        if job not in self.jobs or not job.is_decrypted:
            print(f"Cannot sell job: {job.name}. It is either not owned or not decrypted.")
            return
        if job.data_type not in self.market.categories:
            print(f"Cannot sell job: {job.name}. Unknown category '{job.data_type}'.")
            return

        price = self.market.get_price(job.data_type)
        self.balance += price
        self._record("job_sales", price, job.name)
        self.totals["cogs"] += job.cost
        self.jobs.remove(job)

    def expected_profit(self, job):
        price = self.market.get_price(job.data_type)
        profit = price - job.cost
        pct = (profit / job.cost * 100.0) if job.cost > 0 else 0.0
        return profit, pct

    def _record(self, kind, signed_amount, label):
        self.ledger.append((self.elapsed_time, kind, signed_amount, label))
        self.totals[kind] += abs(signed_amount)

    def current_opex_per_sec(self):
        total = 0.0
        for s in self.servers:
            active = s.state in (ServerState.WORKING, ServerState.OVERHEATED)
            total += s.opex_per_sec * (1.0 if active else s.idle_multiplier)
        return total

    def runway_seconds(self):
        opex = self.current_opex_per_sec()
        return self.balance / opex if opex > 0 else None

    def cashflow_per_minute(self, window=60.0):
        if len(self.balance_history) < 2:
            return 0.0
        t_now, b_now = self.balance_history[-1]
        t_ref, b_ref = self.balance_history[0]
        for t, b in self.balance_history:
            if t_now - t <= window:
                t_ref, b_ref = t, b
                break
        span = t_now - t_ref
        return (b_now - b_ref) / span * 60.0 if span > 0 else 0.0

    def active_server_count(self):
        return sum(1 for s in self.servers if s.state == ServerState.WORKING)

    def _declare_game_over(self, reason):
        self.game_over = True
        self.game_over_reason = reason
        print(f"GAME OVER: {reason}")

    def _check_bankruptcy(self):
        if self.balance < 0:
            self._declare_game_over("Your balance fell below zero.")
            return

        cheapest_server = min(t["capex"] for t in SERVER_CATALOG)
        has_sellable = any(job.is_decrypted for job in self.jobs)
        if not self.servers and not has_sellable and self.balance < cheapest_server:
            self._declare_game_over("You cannot afford a server and have nothing left to sell.")

    def income_statement(self):
        t = self.totals
        revenue = t["job_sales"]
        gross_profit = revenue - t["cogs"]
        operating_result = gross_profit - t["opex"] - t["depreciation"]
        return {
            "revenue": revenue,
            "cogs": t["cogs"],
            "gross_profit": gross_profit,
            "opex": t["opex"],
            "depreciation": t["depreciation"],
            "operating_result": operating_result,
            "disposal_result": t["server_disposal_result"],
            "net_result": operating_result + t["server_disposal_result"],
            "operating_margin": operating_result / revenue * 100.0 if revenue > 0 else None,
        }

    def cashflow_statement(self):
        t = self.totals
        operating = t["job_sales"] - t["job_purchases"] - t["opex"]
        investing = t["server_sales"] - t["server_purchases"]
        return {
            "job_sales": t["job_sales"],
            "job_purchases": t["job_purchases"],
            "opex": t["opex"],
            "operating": operating,
            "server_sales": t["server_sales"],
            "server_purchases": t["server_purchases"],
            "investing": investing,
            "net_change": operating + investing,
        }

    def asset_position(self):
        inventory = sum(job.cost for job in self.jobs)
        servers = sum(s.book_value() for s in self.servers)
        return {
            "cash": self.balance,
            "inventory_at_cost": inventory,
            "servers_at_book": servers,
            "total_assets": self.balance + inventory + servers,
        }

    def cash_reconciliation_error(self):
        return self.balance - (self.starting_balance + self.cashflow_statement()["net_change"])

    def equity_reconciliation_error(self):
        expected = self.starting_balance + self.income_statement()["net_result"]
        return self.asset_position()["total_assets"] - expected

    def update(self, dt):
        if self.game_over:
            return

        self.elapsed_time += dt
        self.market.update(dt)

        for job in self.job_market:
            job.time_left -= dt
        self.job_market = [job for job in self.job_market if job.time_left > 0]
        new_job = self.job_generator.update(dt, len(self.job_market))
        if new_job is not None:
            self.job_market.append(new_job)

        total_opex = 0.0
        total_depreciation = 0.0

        for server in self.servers:
            server.update(dt)
            total_depreciation += server.depreciate(dt)
            if server.state in (ServerState.WORKING, ServerState.OVERHEATED):
                total_opex += server.opex_per_sec * dt
            else:
                total_opex += server.opex_per_sec * server.idle_multiplier * dt

        self.balance -= total_opex
        self.totals["opex"] += total_opex
        self.totals["depreciation"] += total_depreciation

        self._time_since_sample += dt
        if self._time_since_sample >= BALANCE_SAMPLE_INTERVAL:
            self._time_since_sample -= BALANCE_SAMPLE_INTERVAL
            self.balance_history.append((self.elapsed_time, self.balance))

        self._check_bankruptcy()

        