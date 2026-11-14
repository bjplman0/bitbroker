import random
import statistics
from model import EconomyModel, Job, Market, ServerState
from settings import (
    MARKET_CATEGORIES_CONFIG,
    SERVER_BASE_TEMP,
    SERVER_CATALOG,
    SERVER_COOLING_RATE,
    SERVER_HEATING_RATE,
    SERVER_LIFETIME,
    SERVER_SALVAGE_RATIO,
)


def run_section_4_3_reproducibility_and_dt():
    print("=" * 75)
    print("4.3. AUTOMATIZALT SZIMULACIOK: REPRODUKALHATOSAG ES DT-INVARIANCIA")
    print("=" * 75)

    # 1. Reprodukalhatosag (Seed teszt)
    results = []
    for _ in range(2):
        random.seed(42)
        m = EconomyModel(starting_balance=10000.0)
        m.buy_server(SERVER_CATALOG[0])
        for _ in range(1000):
            m.update(0.1)
        prices = [round(c.current_price, 4) for c in m.market.categories.values()]
        results.append((round(m.balance, 4), prices, len(m.job_market)))

    identical = results[0] == results[1]
    print(f"\n[1] Reprodukalhatosagi teszt (random.seed=42, T=100.0s, 1000 lepes):")
    print(f"    1. futtatas: Egyenleg=${results[0][0]}, Piac={results[0][1]}")
    print(f"    2. futtatas: Egyenleg=${results[1][0]}, Piac={results[1][1]}")
    print(f"    Eredmeny: {'PONTOS EGYEZES (Determinisztikus)' if identical else 'ELTERES!'}")

    # 2. Idolepes-invariancia (60 FPS vs 30 FPS vs max dt=0.1s, T = 30.0s folyamatos terheles)
    print("\n[2] Idolepes-invariancia vizsgalat (T = 30.0s folyamatos terheles, Mid Rack):")
    print(f"{'Idolepes (dt)':<18} | {'Iteraciok':>10} | {'Elvegzett munka':>16} | {'Halmozott OPEX':>15} | {'Amortizacio':>13} | {'Zaro hom.':>10}")
    print("-" * 92)

    dt_configs = [
        ("60 FPS (1/60 s)", 1.0 / 60.0, 30 * 60),
        ("30 FPS (1/30 s)", 1.0 / 30.0, 30 * 30),
        ("Max dt (0.10 s)", 0.1, 30 * 10),
    ]

    for label, dt, steps in dt_configs:
        m = EconomyModel(starting_balance=50000.0)
        m.buy_server(SERVER_CATALOG[1])  # Mid Rack (20 speed, 18 opex, max 90 C)
        srv = m.servers[0]
        job = Job("Long-Job", total_work=10000.0, data_type="Military", cost=1000.0)
        m.add_job(job)
        m.assign_job_to_server(0, job)

        for _ in range(steps):
            m.update(dt)

        work_done = 10000.0 - job.remaining_work
        opex = m.totals["opex"]
        dep = m.totals["depreciation"]
        print(f"{label:<18} | {steps:>10} | {work_done:>16.2f} | ${opex:>14.2f} | ${dep:>12.2f} | {srv.temperature:>8.2f} C")


def run_section_4_4_capacity_and_opex():
    print("\n" + "=" * 75)
    print("4.4. KAPACITASKIHASZNALTSAG ES MUKODESI KIADASOK VIZSGALATA")
    print("=" * 75)

    # 1. Analitikus fajlagos mutatok tablazata
    print("\n[1] A szerverkatalogus fajlagos mutatoi es termikus ciklusideje:")
    print(f"{'Szerver modell':<16} | {'CAPEX':>8} | {'Aktiv OPEX':>10} | {'Idle OPEX':>9} | {'k ($/munka)':>11} | {'Amort./s':>8} | {'Melegedesi ido':>14} | {'Hutesi ido':>10}")
    print("-" * 102)

    for tpl in SERVER_CATALOG:
        capex = tpl["capex"]
        opex = tpl["opex"]
        idle_opex = opex * tpl["idle_multiplier"]
        speed = tpl["processing_speed"]
        k = opex / speed
        dep_per_sec = (capex * (1.0 - SERVER_SALVAGE_RATIO)) / SERVER_LIFETIME
        temp_span = tpl["max_temperature"] - SERVER_BASE_TEMP
        t_heat = temp_span / SERVER_HEATING_RATE
        t_cool = temp_span / SERVER_COOLING_RATE

        print(f"{tpl['model']:<16} | ${capex:>7.0f} | ${opex:>7.2f}/s | ${idle_opex:>6.2f}/s | ${k:>10.2f} | ${dep_per_sec:>5.2f}/s | {t_heat:>12.1f} s | {t_cool:>8.1f} s")

    # 2. Kihasznaltsagi (u) erzekenysegvizsgalat (T = 600s, Small Business atlagos arres mellett)
    # Small Business: base_price = 3000, atlagos cost_ratio = 0.75 -> atlagos arres = 750 / 150 munka = $5.00 / munkaegyseg
    sb_cfg = MARKET_CATEGORIES_CONFIG["Small Business"]
    gross_margin_per_work = (sb_cfg["base_price"] * (1.0 - 0.75)) / sb_cfg["job_work_base"]
    sim_duration = 600.0  # 10 perc (teljes amortizacios ciklus)

    print(f"\n[2] Kihasznaltsagi (u) erzekenysegvizsgalat (T = 600s, Small Business ${gross_margin_per_work:.2f}/munka arres mellett):")
    print(f"{'Szerver modell':<16} | {'Kihasznaltsag (u)':>17} | {'Elvegzett munka':>15} | {'Brutto fedezet':>14} | {'Teljes OPEX':>12} | {'Amortizacio':>12} | {'Uzemi eredmeny':>14}")
    print("-" * 112)

    for tpl in SERVER_CATALOG:
        for u_target in [0.10, 0.20, 0.50]:
            # 20 mp-es ciklusokban u_target aranyban dolgozik, (1-u_target) aranyban IDLE (igy nem melegszik tul)
            m = EconomyModel(starting_balance=100000.0)
            m.buy_server(tpl)
            srv = m.servers[0]
            dummy_job = Job("Continuous", total_work=999999.0, data_type="Small Business", cost=0.0)
            m.add_job(dummy_job)

            dt = 0.1
            for step in range(int(sim_duration / dt)):
                cycle_pos = (step * dt) % 20.0
                if cycle_pos < (u_target * 20.0):
                    if srv.state == ServerState.IDLE:
                        srv.start_job(dummy_job)
                else:
                    if srv.current_job is not None:
                        srv.unload_job()
                m.update(dt)

            work_done = 999999.0 - dummy_job.remaining_work
            gross_profit = work_done * gross_margin_per_work
            opex = m.totals["opex"]
            dep = m.totals["depreciation"]
            op_result = gross_profit - opex - dep

            print(f"{tpl['model']:<16} | {u_target * 100:>15.0f} % | {work_done:>15.0f} | ${gross_profit:>13.2f} | ${opex:>11.2f} | ${dep:>11.2f} | ${op_result:>13.2f}")

    # 3. Tulmelegedes vs. Preventiv Unload osszevetese (T = 600s folyamatos munkaigeny)
    print("\n[3] Tulmelegedes (kenyszerhutes) vs. Preventiv Unload osszevetese (T = 600s, Basic Rack):")
    for strategy in ["Kenyszerhutes (Overheat)", "Preventiv Unload (78.5 C-nal)"]:
        m = EconomyModel(starting_balance=100000.0)
        m.buy_server(SERVER_CATALOG[0])  # Basic Rack (max 80 C)
        srv = m.servers[0]
        job = Job("Batch", total_work=999999.0, data_type="Personal", cost=0.0)
        m.add_job(job)
        srv.start_job(job)

        dt = 0.1
        for _ in range(int(600.0 / dt)):
            if strategy.startswith("Preventiv"):
                if srv.state == ServerState.WORKING and srv.temperature >= 78.5:
                    srv.unload_job()
                elif srv.state == ServerState.IDLE and srv.temperature <= SERVER_BASE_TEMP and srv.current_job is None:
                    srv.start_job(job)
            m.update(dt)

        work_done = 999999.0 - job.remaining_work
        opex = m.totals["opex"]
        cost_per_work = opex / work_done if work_done > 0 else 0.0
        print(f"    {strategy:<32} -> Elvegzett munka: {work_done:>6.0f} | Teljes OPEX: ${opex:>7.2f} | Fajlagos OPEX: ${cost_per_work:.3f}/munka")


def run_section_4_5_market_dynamics():
    print("\n" + "=" * 75)
    print("4.5. A PIACI PARAMETEREK HATASA A SZIMULACIO EREDMENYEIRE")
    print("=" * 75)

    # 1. Hosszu tavu AR(1) piaci szimulacio (N = 20 000 masodperc)
    random.seed(12345)
    market = Market()
    n_ticks = 20000
    history = {name: [] for name in MARKET_CATEGORIES_CONFIG}

    for _ in range(n_ticks):
        market.update(1.0)
        for name, cat in market.categories.items():
            history[name].append(cat.current_price)

    print(f"\n[1] Piaci kategoriak sztochasztikus viselkedese (N = {n_ticks} mp, seed=12345):")
    print(f"{'Kategoria':<18} | {'Alapar':>10} | {'Mert atlag':>11} | {'Rel. szoras (CV)':>16} | {'Min/Max korlat (%)':>18} | {'Elmeleti phi':>12} | {'Mert r1':>8}")
    print("-" * 108)

    for name, cfg in MARKET_CATEGORIES_CONFIG.items():
        series = history[name]
        base = cfg["base_price"]
        mean_val = statistics.mean(series)
        stdev_val = statistics.stdev(series)
        cv_pct = (stdev_val / mean_val) * 100.0 if mean_val > 0 else 0.0

        clamp_hits = sum(1 for p in series if p <= cfg["min_price"] or p >= cfg["max_price"])
        clamp_pct = (clamp_hits / n_ticks) * 100.0

        phi_theo = 1.0 - cfg["gravity"]
        diffs = [p - mean_val for p in series]
        num = sum(diffs[i] * diffs[i + 1] for i in range(len(diffs) - 1))
        den = sum(d * d for d in diffs)
        r1 = num / den if den > 0 else 0.0

        print(f"{name:<18} | ${base:>9,.0f} | ${mean_val:>10,.1f} | {cv_pct:>14.2f} % | {clamp_pct:>16.2f} % | {phi_theo:>12.3f} | {r1:>8.3f}")

    # 2. Ertekesitesi strategiak osszevetese UGYANAZON az 500 db Small Business adatcsomagon
    print("\n[2] Ertekesitesi strategiak osszevetese (500 db azonos Small Business adatcsomag):")
    sb_series = history["Small Business"]
    sb_base = MARKET_CATEGORIES_CONFIG["Small Business"]["base_price"]
    random.seed(999)

    total_cost = 0.0
    rev_immediate = 0.0
    rev_timed = 0.0
    total_hold_time = 0

    for i in range(500):
        t_buy = i * 35  # 35 mp-enkent veszunk egy csomagot az idosoron
        buy_market_price = sb_series[t_buy]
        cost_ratio = random.uniform(0.55, 0.95)
        cost = round(buy_market_price * cost_ratio, 2)
        total_cost += cost

        # 30 mp feldolgozas utan (t_ready) elkeszul a csomag
        t_ready = t_buy + 30
        rev_immediate += sb_series[t_ready]

        # Idozito strategia: legfeljebb 120 mp-ig var, amig az ar >= alapar
        hold_sec = 0
        while (t_ready + hold_sec) < (len(sb_series) - 1) and sb_series[t_ready + hold_sec] < sb_base and hold_sec < 120:
            hold_sec += 1

        rev_timed += sb_series[t_ready + hold_sec]
        total_hold_time += hold_sec

    for strat_name, rev, hold in [
        ("Azonnali eladas (dekriptalas utan)", rev_immediate, 0.0),
        ("Arfolyam-idozito (eladas ha P >= P_alap)", rev_timed, total_hold_time / 500.0),
    ]:
        gross_profit = rev - total_cost
        avg_margin_pct = (gross_profit / total_cost) * 100.0
        print(f"    {strat_name:<42} -> Brutto profit: ${gross_profit:>9,.0f} | Atlagos arres: {avg_margin_pct:>5.1f}% | Atl. varakozas: {hold:>4.1f}s")


if __name__ == "__main__":
    run_section_4_3_reproducibility_and_dt()
    run_section_4_4_capacity_and_opex()
    run_section_4_5_market_dynamics()