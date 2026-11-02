import pygame
from settings import FPS, DEFAULT_STARTING_BALANCE
from model import EconomyModel, Server
from view import GameView
from states import DashboardState, MarketplaceState

TAB_KEYS = {
    pygame.K_F1: "dashboard",
    pygame.K_F2: "marketplace",
}

class GameController:
    def __init__(self):
        self.model = EconomyModel(starting_balance=DEFAULT_STARTING_BALANCE)
        self.view = GameView()
        self.clock = pygame.time.Clock()
        self.running = True

        self.states = {
            "dashboard": DashboardState(),
            "marketplace": MarketplaceState(),
        }
        self.active_tab_key = "dashboard"

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
            mouse_pos = pygame.mouse.get_pos()
            self.view.draw(self.model, self.states, self.active_tab_key, mouse_pos)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in TAB_KEYS:
                    self._switch_tab(TAB_KEYS[event.key])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)

    def _switch_tab(self, new_tab_key):
        if new_tab_key == self.active_tab_key:
            return

        self.states[self.active_tab_key].on_exit()
        self.active_tab_key = new_tab_key
        self.states[self.active_tab_key].on_enter()

    def _handle_mouse_click(self, pos):
        for tab_key, rect in self.view.tab_rects.items():
            if rect.collidepoint(pos):
                self._switch_tab(tab_key)
                return

        hit = self.view.get_hit(pos)
        self.states[self.active_tab_key].handle_click(hit, self.model)