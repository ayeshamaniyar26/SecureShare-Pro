"""
Configuration settings for SecureShare Pro
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "SecureShare Pro"
VERSION = "1.0.0"
AUTHOR = "Your Name"  # Change this to your name!

# Directories
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Server Settings
DEFAULT_PORT = 8000
PORT_RANGE = range(8000, 8100)  # Try ports in this range if default is busy

# Ngrok Settings
NGROK_AUTH_TOKEN = None  # Users can add their token for custom domains (optional)

# File Transfer Settings
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB max upload
ALLOWED_FILE_TYPES = None  # None = all files allowed

# History Settings
HISTORY_FILE = LOGS_DIR / "transfer_history.json"
MAX_HISTORY_ENTRIES = 100

# UI Settings
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 600  # Reduced for better visibility
THEME_LIGHT = {
    'bg': '#f0f0f0',
    'fg': '#333333',
    'button_bg': '#4CAF50',
    'button_fg': 'white',
    'accent': '#2196F3'
}
THEME_DARK = {
    'bg': '#2b2b2b',
    'fg': '#ffffff',
    'button_bg': '#4CAF50',
    'button_fg': 'white',
    'accent': '#64B5F6'
}

# Session Settings
DEFAULT_EXPIRATION_MINUTES = 30
AUTO_CLOSE_ON_INACTIVITY = True

# Security Settings
ENABLE_PASSWORD_PROTECTION = True
DEFAULT_PASSWORD = None  # None = no password by default