WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Jatek v0.1"

COLOR_BG = (0, 0, 0)
COLOR_TERMINAL_GREEN = (0, 255, 0)
COLOR_PANEL_BORDER = (40, 40, 40)

DEFAULT_STARTING_BALANCE = 5000.0

SERVER_BASE_TEMP = 30.0
SERVER_HEATING_RATE = 0.1
SERVER_COOLING_RATE = 0.2

MARKET_TICK_RATE = 1.0

MARKET_CATEGORIES_CONFIG = {
    "Personal": {
        "base_price": 100.0,
        "volatility": 0.1,
        "gravity": 0.05
    },
    "Small Business": {
        "base_price": 1000.0,
        "volatility": 0.2,
        "gravity": 0.1
    },
    "Large Corporation": {
        "base_price": 10000.0,
        "volatility": 0.3,
        "gravity": 0.2
    },
    "Government": {
        "base_price": 10000.0,
        "volatility": 0.3,
        "gravity": 0.2
    },
    "Military": {
        "base_price": 100000.0,
        "volatility": 0.4,
        "gravity": 0.3
    }
}