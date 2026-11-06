"""
Fish Quest - Ocean Adventure Game
Configuration and Global Settings Module

Demonstrates: Low Coupling and High Cohesion
By centralizing all environment, UI, gameplay, and network configuration constants,
individual modules remain decoupled from hardcoded values.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
FONTS_DIR = ASSETS_DIR / "fonts"

# Database Configuration
DATABASE_PATH = BASE_DIR / "fish_quest.db"

# Window & Display Settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 680
FPS = 60
WINDOW_TITLE = "Fish Quest – Ocean Adventure"

# Color Palette (Underwater & Modern Oceanic Theme)
COLOR_DEEP_OCEAN_DARK = (8, 20, 38)
COLOR_OCEAN_NAVY      = (15, 32, 67)
COLOR_OCEAN_BLUE      = (22, 53, 98)
COLOR_SURFACE_BLUE    = (35, 78, 138)
COLOR_AQUA_ACCENT     = (34, 211, 238)
COLOR_TEAL            = (20, 184, 166)
COLOR_GOLD            = (250, 204, 21)
COLOR_GOLD_DARK       = (217, 119, 6)
COLOR_CORAL_RED       = (244, 63, 94)
COLOR_SUCCESS_GREEN   = (34, 197, 94)
COLOR_CARD_BG         = (18, 38, 72, 220)       # Semi-transparent card
COLOR_CARD_BORDER     = (56, 189, 248)
COLOR_CARD_DARK       = (12, 26, 50, 235)
COLOR_TEXT_PRIMARY    = (248, 250, 252)
COLOR_TEXT_SECONDARY  = (148, 163, 184)
COLOR_TEXT_MUTED      = (100, 116, 139)
COLOR_INPUT_BG        = (10, 24, 48)
COLOR_INPUT_BORDER    = (56, 189, 248)
COLOR_INPUT_FOCUS     = (14, 165, 233)
COLOR_OVERLAY         = (5, 12, 24, 190)

# Button Color Themes
BTN_PRIMARY = {
    "normal": (14, 165, 233),
    "hover": (56, 189, 248),
    "pressed": (2, 132, 199),
    "text": (255, 255, 255),
    "border": (125, 211, 252)
}

BTN_SUCCESS = {
    "normal": (16, 185, 129),
    "hover": (52, 211, 153),
    "pressed": (5, 150, 105),
    "text": (255, 255, 255),
    "border": (110, 231, 183)
}

BTN_DANGER = {
    "normal": (239, 68, 68),
    "hover": (248, 113, 113),
    "pressed": (220, 38, 38),
    "text": (255, 255, 255),
    "border": (252, 165, 165)
}

BTN_SECONDARY = {
    "normal": (30, 58, 102),
    "hover": (45, 84, 145),
    "pressed": (20, 42, 75),
    "text": (226, 232, 240),
    "border": (71, 115, 180)
}

BTN_WARNING = {
    "normal": (217, 119, 6),
    "hover": (245, 158, 11),
    "pressed": (180, 83, 9),
    "text": (255, 255, 255),
    "border": (253, 230, 138)
}

# External API Configuration
API_BASE_URL = "http://marcconrad.com/uob/fish/api.php"
API_TIMEOUT_SECONDS = 10
API_DEFAULT_PARAMS = {"out": "json"}

# Gameplay Mechanics
INITIAL_LIVES = 3
POINTS_PER_CORRECT = 10
COINS_PER_CORRECT = 5
BASE_COUNTDOWN_SECONDS = 25
MIN_COUNTDOWN_SECONDS = 10
TIME_DECREASE_PER_LEVEL = 2
QUESTIONS_PER_LEVEL = 3
STREAK_BONUS_THRESHOLD = 3
STREAK_BONUS_POINTS = 5

