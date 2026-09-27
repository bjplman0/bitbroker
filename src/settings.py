SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
#WINDOW_TITLE = "Jatek v0.1"
CAPTION = "Jatek v0.1"

COLOR_BG = (0, 0, 0)
COLOR_PANEL = (15, 25, 15)
COLOR_BORDER = (40, 120, 40)
COLOR_TEXT = (50, 205, 50)

FONT_PATH = "src/VT323-Regular.ttf"
FONT_SIZE = 24

DEFAULT_STARTING_BALANCE = 5000.0

SERVER_BASE_TEMP = 30.0
SERVER_HEATING_RATE = 0.1
SERVER_COOLING_RATE = 0.2

MARKET_TICK_RATE = 1.0

MARKET_CATEGORIES_CONFIG = {
    "Personal": {
        "base_price": 250.0,
        "volatility": 0.015,
        "gravity": 0.005,
        "min_price": 50.0,
        "max_price": 600.0
    },
    "Small Business": {
        "base_price": 4500.0,
        "volatility": 0.02,
        "gravity": 0.008,
        "min_price": 1500.0,
        "max_price": 12000.0
    },
    "Large Corporation": {
        "base_price": 55000.0,
        "volatility": 0.04,
        "gravity": 0.002,
        "min_price": 10000.0,
        "max_price": 160000.0
    },
    "Government": {
        "base_price": 55000.0,
        "volatility": 0.008,
        "gravity": 0.05,
        "min_price": 45000.0,
        "max_price": 70000.0
    },
    "Military": {
        "base_price": 1500000.0,
        "volatility": 0.025,
        "gravity": 0.005,
        "min_price": 500000.0,
        "max_price": 4500000.0
    }
}

#copy notes from textbook to here or to a separate file for reference
