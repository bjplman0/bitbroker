import pygame
from settings import FPS, DEFAULT_STARTING_BALANCE
from model import EconomyModel
from view import GameView
from states import DashboardState, MarketplaceState, FinancialState
from repository import SaveRepository

TAB_KEYS = {
    pygame.K_F1: "dashboard",
    pygame.K_F2: "marketplace",
    pygame.K_F3: "financial",
}

class GameController:
    def __init__(self):
        self.view = GameView()
        self.clock = pygame.time.Clock()
        self.running = True
        self.repo = SaveRepository()

        self.states = {
            "dashboard": DashboardState(),
            "marketplace": MarketplaceState(),
            "financial": FinancialState(),
        }
        self.active_tab_key = "dashboard"
        self.model = EconomyModel(starting_balance=DEFAULT_STARTING_BALANCE)
        self.mode = "menu"
        self.paused = False

    def _new_game(self):
        self.repo.delete()
        self.model = EconomyModel(starting_balance=DEFAULT_STARTING_BALANCE)
        for state in self.states.values():
            state.on_exit()
        self.active_tab_key = "dashboard"
        self.paused = False
        self.mode = "playing"

    def _continue_game(self):
        loaded_model = self.repo.load()
        if loaded_model is not None:
            self.model = loaded_model
            for state in self.states.values():
                state.on_exit()
            self.active_tab_key = "dashboard"
            self.paused = False
            self.mode = "playing"

    def _save_and_quit_to_menu(self):
        if not self.model.game_over:
            self.repo.save(self.model)
        for state in self.states.values():
            state.on_exit()
        self.paused = False
        self.mode = "menu"

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.1)
            self.handle_events()
            if (self.mode == "playing" and not self.paused and not self.model.game_over):
                self.model.update(dt)
                if self.model.game_over:
                    self.repo.delete()

            mouse_pos = pygame.mouse.get_pos()
            if self.mode == "menu":
                self.view.draw_main_menu(mouse_pos, self.repo.exists())
            else:
                self.view.draw(self.model, self.states, self.active_tab_key, mouse_pos, paused=self.paused,)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.mode == "menu":
                    continue
                if self.model.game_over:
                    if event.key == pygame.K_r:
                        self._new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.mode = "menu"
                elif event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif not self.paused and event.key in TAB_KEYS:
                    self._switch_tab(TAB_KEYS[event.key])

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click(event.pos)

    def _switch_tab(self, new_tab_key):
        if new_tab_key == self.active_tab_key:
            return
        self.states[self.active_tab_key].on_exit()
        self.active_tab_key = new_tab_key
        self.states[self.active_tab_key].on_enter()

    def _handle_mouse_click(self, pos):
        hit = self.view.get_hit(pos)
        if self.mode == "menu":
            if hit is None:
                return
            kind, _ = hit
            if kind == "menu_new":
                self._new_game()
            elif kind == "menu_continue":
                self._continue_game()
            elif kind == "menu_quit":
                self.running = False
            return
        
        if self.model.game_over:
            hit = self.view.get_hit(pos)
            if hit and hit[0] == "restart":
                self._new_game()
            elif hit and hit[0] == "game_over_menu":
                self.mode = "menu"
            return

        if self.paused:
            if hit is None:
                return
            kind, _ = hit
            if kind == "pause_resume":
                self.paused = False
            elif kind == "pause_save_quit":
                self._save_and_quit_to_menu()
            return

        for tab_key, rect in self.view.tab_rects.items():
            if rect.collidepoint(pos):
                self._switch_tab(tab_key)
                return

        self.states[self.active_tab_key].handle_click(hit, self.model)