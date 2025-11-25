import os
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent

class Config:
    """Application configuration."""
    
    # Paths
    NSJAIL_CONFIG_PATH = str(_APP_DIR / "execution" / "nsjail.cfg")
    SANDBOX_ROOT = Path(os.getenv("SANDBOX_ROOT", "/tmp/nsjail_exec"))
    
    # Resource limits
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "5")) # 30 seconds
    MAX_SCRIPT_LENGTH = int(os.getenv("MAX_SCRIPT_LENGTH", "20000")) # 20000 characters
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "20971520"))  # 20MB default

