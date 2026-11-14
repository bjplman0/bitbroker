from pathlib import Path
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
CAPTION = "BitBroker"
BASE_DIR = Path(__file__).resolve().parent
SAVE_FILE_PATH = str(BASE_DIR.parent / "savegame.json")


#colors
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
COLOR_ROW_HOVER = (25, 50, 25)
OVERLAY_ALPHA = 200

#font
FONT_PATH = str(BASE_DIR / "VT323-Regular.ttf")
FONT_SIZE = 32
FONT_SIZE_SMALL = 20

#general layout and ui
TAB_BAR_HEIGHT = 50
TAB_TEXT_Y = 12
CARD_RADIUS = 6
TAB_ITEM_SPACING = 40
PANEL_PADDING = 20
SECTION_GAP = 20
SECTION_GAP_LARGE = 30
BAR_RADIUS = 4

#dashboard
DASHBOARD_MARKET_RATIO = 0.3
DASHBOARD_SERVER_RATIO = 0.5
DASHBOARD_FINANCE_RATIO = 0.2

#market layout
MARKET_CARD_HEIGHT = 178
MARKET_CARD_GAP = 6
MARKET_MIN_SPAN_RATIO = 0.02
MARKET_CHART_PAD_RATIO = 0.12
DASH_LENGTH = 6
DASH_GAP = 5

#server layout
RACK_HEIGHT = 150
RACK_PADDING = 20
SERVER_BAR_HEIGHT = 16
SERVER_BTN_WIDTH = 85
SERVER_BTN_HEIGHT = 30

#owned jobs and tables
OWNED_ROW_HEIGHT = 56
ROW_HEIGHT = 44
TABLE_MARGIN = 20
STATEMENT_ROW_HEIGHT = 34

#financial layout
KPI_CARD_HEIGHT = 100
BALANCE_CHART_HEIGHT = 250
BALANCE_CHART_PAD_RATIO = 0.10
RUNWAY_WARN_SEC = 60.0
RUNWAY_MAX_DISPLAY_SEC = 3600.0
JOB_EXPIRY_WARN_SEC = 10.0

#menu layouts
MENU_BOX_WIDTH = 520
MENU_BOX_HEIGHT = 440
MENU_BTN_WIDTH = 320
MENU_BTN_HEIGHT = 60
MENU_BTN_GAP = 25

PAUSE_BOX_WIDTH = 520
PAUSE_BOX_HEIGHT = 320
PAUSE_BTN_WIDTH = 360
PAUSE_BTN_HEIGHT = 60

GAME_OVER_BOX_WIDTH = 800
GAME_OVER_BOX_HEIGHT = 420
GAME_OVER_BTN_WIDTH = 280
GAME_OVER_BTN_HEIGHT = 60
GAME_OVER_BTN_OFFSET_X = 160

#table columns
JOB_COLUMNS = [
    ("NAME",     0.00, "left"),
    ("CATEGORY", 0.28, "left"),
    ("WORK",     0.50, "right"),
    ("COST",     0.64, "right"),
    ("PROFIT",   0.82, "right"),
    ("EXPIRES",  0.97, "right"),
]

SHOP_COLUMNS = [
    ("MODEL",    0.00, "left"),
    ("SPEED",    0.45, "right"),
    ("MAX TEMP", 0.58, "right"),
    ("OPEX",     0.70, "right"),
    ("COST",     0.85, "right"),
]

#simulation parameters
DEFAULT_STARTING_BALANCE = 5000.0

MAX_SERVERS = 5
SERVER_BASE_TEMP = 30.0
SERVER_HEATING_RATE = 1.2
SERVER_COOLING_RATE = 2.0
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
MAX_OWNED_JOBS = 8

MILITARY_NUM_MIN = 1
MILITARY_NUM_MAX = 99

BALANCE_SAMPLE_INTERVAL = 1.0
BALANCE_HISTORY_LENGTH = 300
LEDGER_MAX_ENTRIES = 200
CASHFLOW_WINDOW = 60.0

MARKET_TICK_RATE = 1.0
MARKET_HISTORY_LENGTH = 30

#catalogs
SERVER_CATALOG = [
    {
        "model": "Basic Rack",
        "capex": 1500.0,
        "opex": 5.0,
        "processing_speed": 5.0,
        "max_temperature": 80.0,
        "idle_multiplier": 0.20
    },
    {
        "model": "Mid Rack",
        "capex": 6000.0,
        "opex": 18.0,
        "processing_speed": 20.0,
        "max_temperature": 90.0,
        "idle_multiplier": 0.25
    },
    {
        "model": "Enterprise Rack",
        "capex": 25000.0,
        "opex": 50.0,
        "processing_speed": 80.0,
        "max_temperature": 100.0,
        "idle_multiplier": 0.30
    }
]

MARKET_CATEGORIES_CONFIG = {
    "Personal": {
        "base_price": 600.0,
        "volatility": 0.015,
        "gravity": 0.005,
        "min_price": 200.0,
        "max_price": 1200.0,
        "job_work_base": 30.0
    },
    "Small Business": {
        "base_price": 3000.0,
        "volatility": 0.02,
        "gravity": 0.008,
        "min_price": 1000.0,
        "max_price": 6000.0,
        "job_work_base": 150.0
    },
    "Large Corporation": {
        "base_price": 15000.0,
        "volatility": 0.04,
        "gravity": 0.002,
        "min_price": 4000.0,
        "max_price": 45000.0,
        "job_work_base": 600.0
    },
    "Government": {
        "base_price": 25000.0,
        "volatility": 0.008,
        "gravity": 0.05,
        "min_price": 20000.0,
        "max_price": 32000.0,
        "job_work_base": 900.0
    },
    "Military": {
        "base_price": 120000.0,
        "volatility": 0.025,
        "gravity": 0.005,
        "min_price": 40000.0,
        "max_price": 300000.0,
        "job_work_base": 2000.0
    }
}


