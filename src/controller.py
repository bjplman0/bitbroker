import pygame
from settings import FPS, DEFAULT_STARTING_BALANCE
from model import EconomyModel, Server
from view import GameView

class GameController:
    def __init__(self):
        self.model = EconomyModel(starting_balance=DEFAULT_STARTING_BALANCE)
        self.view = GameView()
        self.clock = pygame.time.Clock()
        self.running = True

        self._create_test_servers()

    def _create_test_servers(self):
        server1 = Server(
            name="Server-01",
            capex=1000.0,
            opex=15.0,
            processing_speed=50.0,
            max_temperature=95.0,
            idle_multiplier=0.2
        )
        self.model.add_server(server1)

        server2 = Server(
            name="Server-02",
            capex=1500.0,
            opex=22.0,
            processing_speed=75.0,
            max_temperature=90.0,
            idle_multiplier=0.25
        )
        self.model.add_server(server2)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.model.update(dt)
            self.view.draw(self.model)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False