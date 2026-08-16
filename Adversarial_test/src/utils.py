"""
Utility functions for the adversarial test framework.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

def create_timestamp() -> str:
    """Create a timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(path: str) -> str:
    """Ensure a directory exists and return the path."""
    os.makedirs(path, exist_ok=True)
    return path

def load_json(filepath: str) -> Dict[str, Any]:
    """Load a JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {filepath}: {e}")
        return {}

def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> bool:
    """Save data to JSON file safely."""
    try:
        ensure_dir(os.path.dirname(filepath))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save JSON: {e}")
        return False

def progress_bar(iteration: int, total: int, prefix: str = "", suffix: str = "", length: int = 40) -> str:
    """Create a progress bar string."""
    percent = iteration / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"{prefix} |{bar}| {iteration}/{total} {suffix}"

def get_memory_usage() -> Optional[int]:
    """Get current memory usage in MB, if available."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return None
    except Exception:
        return None
