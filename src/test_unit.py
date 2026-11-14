import os
import tempfile
import unittest
from model import EconomyModel, Job, Server, ServerState
from repository import SaveRepository
from settings import (
    DEFAULT_STARTING_BALANCE,
    MAX_OWNED_JOBS,
    MAX_SERVERS,
    SERVER_BASE_TEMP,
    SERVER_CATALOG,
    SERVER_HEATING_RATE,
    SERVER_LIFETIME,
    SERVER_RESALE_RATIO,
    SERVER_SALVAGE_RATIO,
)


class TestEconomyVerification(unittest.TestCase):

    def setUp(self):
        self.economy = EconomyModel(starting_balance=DEFAULT_STARTING_BALANCE)
        self.basic_template = SERVER_CATALOG[0]

    def test_01_new_game_initial_state(self):
        # FK-01: Kezdeti allapot
        self.assertEqual(self.economy.balance, DEFAULT_STARTING_BALANCE)
        self.assertEqual(len(self.economy.servers), 0)
        self.assertEqual(len(self.economy.jobs), 0)
        self.assertEqual(self.economy.elapsed_time, 0.0)
        self.assertFalse(self.economy.game_over)

    def test_02_server_state_machine_and_temperature(self):
        # FK-05, FK-06, FK-07, FK-08: Szerver allapotgep, melegedes, hules, Unload
        server = Server(
            name="Server-01",
            capex=1500.0,
            opex=5.0,
            processing_speed=5.0,
            max_temperature=80.0,
            idle_multiplier=0.2,
        )
        self.economy.add_server(server)

        job = Job(name="Test-Job", total_work=1000.0, data_type="Personal", cost=100.0)
        self.economy.add_job(job)
        self.economy.assign_job_to_server(0, job)

        self.assertEqual(server.state, ServerState.WORKING)

        # 10 masodperc munka: homerseklet 30 + 10 * 1.2 = 42.0 C, munka 1000 - 50 = 950
        self.economy.update(10.0)
        self.assertAlmostEqual(server.temperature, 30.0 + 10.0 * SERVER_HEATING_RATE)
        self.assertAlmostEqual(job.remaining_work, 950.0)

        # Unload WORKING allapotban -> IDLE lesz, munka megmarad 950-en (FK-06)
        self.economy.unload_server(server)
        self.assertEqual(server.state, ServerState.IDLE)
        self.assertIsNone(server.current_job)
        self.assertAlmostEqual(job.remaining_work, 950.0)

        # Visszateszem a munkat es tulmelegitem (42 C -> >80 C-hoz kell >31.67 mp, pl. 35 mp)
        self.economy.assign_job_to_server(0, job)
        self.economy.update(35.0)
        self.assertEqual(server.state, ServerState.OVERHEATED)

        # Tulmelegedett allapotban a munka nem halad, de a teljes OPEX (5/s) vonodik
        work_before = job.remaining_work
        balance_before = self.economy.balance
        self.economy.update(5.0)
        self.assertEqual(job.remaining_work, work_before)
        self.assertAlmostEqual(self.economy.balance, balance_before - 5.0 * server.opex_per_sec)

        # Unload OVERHEATED allapotban -> a szervernek OVERHEATED-ben kell maradnia! (FK-06)
        self.economy.unload_server(server)
        self.assertIsNone(server.current_job)
        self.assertEqual(server.state, ServerState.OVERHEATED)

        # Teljes lehules utan (2.0 C/s-al 30 mp alatt) visszavalt IDLE-be
        self.economy.update(30.0)
        self.assertEqual(server.temperature, SERVER_BASE_TEMP)
        self.assertEqual(server.state, ServerState.IDLE)

    def test_03_job_completion_priority_over_overheat(self):
        # FK-07: Ha a munka pont abban a lepesben keszul el, amikor tulmelegedne, IDLE lesz
        server = Server("Server-01", 1500.0, 5.0, 5.0, 40.0, 0.2)
        job = Job("Fast-Job", total_work=50.0, data_type="Personal", cost=50.0)
        server.start_job(job)

        # 10 mp alatt 50 munkat vegez (lenullazza), homerseklet 30 + 12 = 42.0 C (>40.0) lenne
        server.update(10.0)
        self.assertTrue(job.is_decrypted)
        self.assertEqual(job.remaining_work, 0.0)
        self.assertEqual(server.state, ServerState.IDLE)

    def test_04_limits_and_expiration(self):
        # FK-02, FK-03, FK-04: Keszletkorlatok, fedezethiany, lejaro ajanlatok
        self.economy.balance = 100000.0

        # MAX_SERVERS (5 db) korlat tesztelese
        for _ in range(MAX_SERVERS + 2):
            self.economy.buy_server(self.basic_template)
        self.assertEqual(len(self.economy.servers), MAX_SERVERS)

        # MAX_OWNED_JOBS (8 db) korlat tesztelese
        for i in range(MAX_OWNED_JOBS + 2):
            j = Job(f"Job-{i}", 30.0, "Personal", cost=10.0, lifetime=50.0)
            self.economy.job_market.append(j)
            self.economy.buy_job(j)
        self.assertEqual(len(self.economy.jobs), MAX_OWNED_JOBS)

        # Lejaro ajanlat torlese a piacrol (FK-02)
        expiring_job = Job("Expiring", 30.0, "Personal", cost=10.0, lifetime=2.0)
        self.economy.job_market = [expiring_job]
        self.economy.update(3.0)
        self.assertEqual(len(self.economy.job_market), 0)

    def test_05_depreciation_and_server_disposal(self):
        # FK-10: Linearis ertekcsokkenes a maradvanyertekig es ertekesites
        self.economy.buy_server(self.basic_template)
        server = self.economy.servers[0]
        capex = server.capex
        salvage = capex * SERVER_SALVAGE_RATIO  # 1500 * 0.2 = 300

        # Futtatas 300 mp-ig (fel elettartam): konyv szerinti ertek 1500 - 600 = 900
        total_dep_half = server.depreciate(SERVER_LIFETIME / 2.0)
        self.assertAlmostEqual(total_dep_half, (capex - salvage) / 2.0)
        self.assertAlmostEqual(server.book_value(), 900.0)

        # Futtatas a teljes elettartamon tul (meg 500 mp): nem mehet 300 ala!
        total_dep_rest = server.depreciate(500.0)
        self.assertAlmostEqual(total_dep_half + total_dep_rest, capex - salvage)
        self.assertAlmostEqual(server.book_value(), salvage)

        # Eladas IDLE allapotban: eladasi ar = 300 * 0.8 = 240, kivezetesi eredmeny = 240 - 300 = -60
        expected_sell = salvage * SERVER_RESALE_RATIO
        self.economy.sell_server(server)
        self.assertAlmostEqual(self.economy.totals["server_sales"], expected_sell)
        self.assertAlmostEqual(
            self.economy.totals["server_disposal_result"], expected_sell - salvage
        )

    def test_06_bankruptcy_conditions(self):
        # FK-14: Csodfeltetelek (negativ egyenleg, operativ zsakutca)
        # 1. Operativ zsakutca: nincs szerver, nincs eladhato munka, egyenleg < 1500
        model_deadlock = EconomyModel(starting_balance=1000.0)
        model_deadlock.update(0.1)
        self.assertTrue(model_deadlock.game_over)

        # 2. Negativ egyenleg OPEX miatt
        model_neg = EconomyModel(starting_balance=1505.0)
        model_neg.buy_server(self.basic_template)  # Marad 5 dollar
        model_neg.update(10.0)  # Idle OPEX: 5 * 0.2 * 10 = 10 dollar -> -5 dollar
        self.assertLess(model_neg.balance, 0.0)
        self.assertTrue(model_neg.game_over)

    def test_07_persistence_and_reference_integrity(self):
        # FK-16, FK-17, FK-18: JSON mentes, visszatoltes es objektumreferencia megorzese
        self.economy.buy_server(self.basic_template)
        j0 = Job("Job-0", 100.0, "Personal", cost=100.0)
        j1 = Job("Job-1", 150.0, "Small Business", cost=500.0)
        self.economy.add_job(j0)
        self.economy.add_job(j1)
        self.economy.assign_job_to_server(0, j1)
        self.economy.update(5.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_save.json")
            repo = SaveRepository(filepath=save_path)

            self.assertTrue(repo.save(self.economy))
            self.assertTrue(repo.exists())

            loaded = repo.load()
            self.assertIsNotNone(loaded)
            self.assertAlmostEqual(loaded.balance, self.economy.balance)
            self.assertEqual(len(loaded.jobs), 2)
            self.assertEqual(len(loaded.servers), 1)

            # Ellenorzes: a szerver current_job referenciaja UGYANAZ a peldany, mint a jobs[1]
            self.assertIs(loaded.servers[0].current_job, loaded.jobs[1])

            # Serult JSON fajl kezelese (FK-18)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("{corrupted_json: ")
            self.assertFalse(repo.exists())
            self.assertIsNone(repo.load())

    def test_08_accounting_reconciliation_identities(self):
        # FK-12: Penzugyi es merlegegyezosegi azonossagok (epszilon_K es epszilon_A)
        self.economy.balance = 20000.0
        self.economy.starting_balance = 20000.0

        # 1. Szerverek vasarlasa
        self.economy.buy_server(SERVER_CATALOG[0])  # Basic
        self.economy.buy_server(SERVER_CATALOG[1])  # Mid

        # 2. Munkak vasarlasa
        j1 = Job("Job-A", 50.0, "Personal", cost=150.0, lifetime=40.0)
        j2 = Job("Job-B", 150.0, "Small Business", cost=3000.0, lifetime=40.0)
        self.economy.job_market.extend([j1, j2])
        self.economy.buy_job(j1)
        self.economy.buy_job(j2)

        # 3. Feldolgozas inditasa es vegyes idolepesek futtatasa
        self.economy.assign_job_to_server(0, j1)
        self.economy.assign_job_to_server(1, j2)

        for _ in range(120):
            self.economy.update(0.1)
            self.assertLess(abs(self.economy.cash_reconciliation_error()), 1e-9)
            self.assertLess(abs(self.economy.equity_reconciliation_error()), 1e-9)

        # 4. Elkeszult munkak eladasa (COGS es arbevetel elszamolasa)
        self.assertTrue(j1.is_decrypted)
        self.assertTrue(j2.is_decrypted)
        self.economy.sell_job(j1)
        self.economy.sell_job(j2)

        # 5. Egyik szerver eladasa (kivezetesi veszteseg elszamolasa)
        self.economy.sell_server(self.economy.servers[0])

        self.assertLess(abs(self.economy.cash_reconciliation_error()), 1e-9)
        self.assertLess(abs(self.economy.equity_reconciliation_error()), 1e-9)


if __name__ == "__main__":
    unittest.main(verbosity=2)