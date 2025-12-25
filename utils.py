"""
Utility functions for SecureShare Pro
"""

import json
import socket
import qrcode
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
import config


def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def find_free_port(start_port=None):
    """Find an available port to use"""
    start = start_port or config.DEFAULT_PORT
    for port in range(start, start + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None


def generate_qr_code(url, size=300):
    """Generate QR code for the given URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def format_bytes(bytes_num):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} PB"


def format_time(seconds):
    """Convert seconds to human readable time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def save_transfer_history(file_path, url, mode, timestamp=None):
    """Save transfer history to JSON file"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    history = load_transfer_history()

    entry = {
        'timestamp': timestamp,
        'file_path': str(file_path),
        'url': url,
        'mode': mode,
        'size': get_file_size(file_path)
    }

    history.append(entry)

    # Keep only last MAX_HISTORY_ENTRIES
    if len(history) > config.MAX_HISTORY_ENTRIES:
        history = history[-config.MAX_HISTORY_ENTRIES:]

    try:
        with open(config.HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")


def load_transfer_history():
    """Load transfer history from JSON file"""
    if not config.HISTORY_FILE.exists():
        return []

    try:
        with open(config.HISTORY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def get_file_size(path):
    """Get total size of file or directory"""
    path = Path(path)
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return 0


def validate_path(path):
    """Validate if path exists and is accessible"""
    path = Path(path)
    return path.exists() and (path.is_file() or path.is_dir())


def get_file_count(path):
    """Get number of files in a directory"""
    path = Path(path)
    if path.is_file():
        return 1
    elif path.is_dir():
        return len([f for f in path.rglob('*') if f.is_file()])
    return 0
