from model import EconomyModel, Job, Server, Market

def run_test():
    print("\n---- 1. Initializing ----")
    economy = EconomyModel(5000.0)

    server = Server(
        name = "Test Server",
        capex = 1000.0,
        opex = 15.0,
        processing_speed = 50.0,
        max_temperature = 95.0,
        idle_multiplier = 0.2
    )
    economy.add_server(server)

    job = Job(
        name = "Test Job",
        total_work = 200.0,
        data_type = "Small Business"
    )
    economy.add_job(job)

    print(f"Starting balance: ${economy.balance:.2f}")

    print("\n---- 2. Starting Job ----")
    server.start_job(job)

    print("\n---- 3. Simulating at 60 fps----")
    fps = 60.0
    dt = 1.0 / fps
    frame_count = 0

    while not job.is_decrypted:
        economy.update(dt)
        frame_count += 1
        if frame_count % fps == 0:
            print(f"[Time: {frame_count // fps} sec]"
                  f"Balance: ${economy.balance:.2f} | "
                  f"Server Temperature: {server.temperature:.1f} | "
                  f"Job Remaining Work: {job.remaining_work:.1f}"
                  )

    print("\n---- 4. Waiting for market (3 sec) ----")

    for i in range(int(3 * fps)):
        economy.update(dt)
        frame_count += 1
        if frame_count % fps == 0:
            current_price = economy.market.get_price(job.data_type)
            print(f"[Time: {frame_count // fps} sec]"
                  f"Balance: ${economy.balance:.2f} | "
                  f"{job.data_type} Market Price: ${current_price:.2f}"
                  )

    print("\n---- 5. Selling Job ----")
    economy.sell_job(job)
    print(f"New balance: ${economy.balance:.2f}")

if __name__ == "__main__":
    run_test()