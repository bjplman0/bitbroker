SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
CAPTION = "Jatek v0.1"
SAVE_FILE_PATH = "savegame.json"

COLOR_BG = (0, 0, 0)
COLOR_PANEL = (15, 25, 15)
COLOR_PANEL_LIGHT = (20, 35, 20)
COLOR_BORDER = (40, 120, 40)
COLOR_TEXT = (50, 205, 50)
COLOR_TEXT_DIM = (30, 110, 30)
COLOR_WORKING = (50, 205, 50)
COLOR_OVERHEAT = (255, 70, 70)
COLOR_IDLE = (90, 130, 90)
COLOR_SELECT = (160, 255, 160)
COLOR_WARN = (230, 170, 50)

OWNED_ROW_HEIGHT = 56
TAB_BAR_HEIGHT = 50
CARD_RADIUS = 6

ROW_HEIGHT = 44
TABLE_MARGIN = 20
COLOR_ROW_HOVER = (25, 50, 25)

FONT_PATH = "src/VT323-Regular.ttf"
FONT_SIZE = 32
FONT_SIZE_SMALL = 20

DEFAULT_STARTING_BALANCE = 5000.0

MAX_SERVERS = 5
SERVER_BASE_TEMP = 30.0
SERVER_HEATING_RATE = 0.1
SERVER_COOLING_RATE = 0.2
SERVER_RESALE_RATIO = 0.8
SERVER_LIFETIME = 600.0
SERVER_SALVAGE_RATIO = 0.2

JOB_GENERATION_INTERVAL = 4.0
JOB_POOL_MAX_SIZE = 6
JOB_WORK_VARIANCE = 0.3
JOB_COST_RATIO_MIN = 0.55
JOB_COST_RATIO_MAX = 0.95
JOB_LIFETIME_MIN = 25.0
JOB_LIFETIME_MAX = 60.0

BALANCE_SAMPLE_INTERVAL = 1.0
BALANCE_HISTORY_LENGTH = 300
LEDGER_MAX_ENTRIES = 200

SERVER_CATALOG = [
    {
        "model": "Basic Rack",
        "capex": 1500.0,
        "opex": 10.0,
        "processing_speed": 5.0,
        "max_temperature": 80.0,
        "idle_multiplier": 0.20
    },
    {
        "model": "Mid Rack",
        "capex": 6000.0,
        "opex": 25.0,
        "processing_speed": 15.0,
        "max_temperature": 90.0,
        "idle_multiplier": 0.25
    },
    {
        "model": "Enterprise Rack",
        "capex": 25000.0,
        "opex": 70.0,
        "processing_speed": 45.0,
        "max_temperature": 100.0,
        "idle_multiplier": 0.30
    }
]

MARKET_TICK_RATE = 1.0
MARKET_HISTORY_LENGTH = 30

MARKET_CATEGORIES_CONFIG = {
    "Personal": {
        "base_price": 250.0,
        "volatility": 0.015,
        "gravity": 0.005,
        "min_price": 50.0,
        "max_price": 600.0,
        "job_work_base": 30.0
    },
    "Small Business": {
        "base_price": 4500.0,
        "volatility": 0.02,
        "gravity": 0.008,
        "min_price": 1500.0,
        "max_price": 12000.0,
        "job_work_base": 150.0
    },
    "Large Corporation": {
        "base_price": 55000.0,
        "volatility": 0.04,
        "gravity": 0.002,
        "min_price": 10000.0,
        "max_price": 160000.0,
        "job_work_base": 600.0
    },
    "Government": {
        "base_price": 55000.0,
        "volatility": 0.008,
        "gravity": 0.05,
        "min_price": 45000.0,
        "max_price": 70000.0,
        "job_work_base": 900.0
    },
    "Military": {
        "base_price": 1500000.0,
        "volatility": 0.025,
        "gravity": 0.005,
        "min_price": 500000.0,
        "max_price": 4500000.0,
        "job_work_base": 2000.0
    }
}


