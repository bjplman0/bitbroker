import pygame
from settings import FPS, DEFAULT_STARTING_BALANCE
from model import EconomyModel
from view import GameView

class GameController:
    def __init__(self):
        self.model = EconomyModel(starting_balance=DEFAULT_STARTING_BALANCE)
        self.view = GameView()
        self.clock = pygame.time.Clock()
        self.running = True

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