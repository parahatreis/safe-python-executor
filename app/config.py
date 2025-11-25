import os
from pathlib import Path


class Config:
    """Application configuration."""
    
    NSJAIL_CONFIG_PATH = str(Path(__file__).parent / "execution" / "nsjail_config.cfg")
    NSJAIL_ENABLED = os.getenv("ENABLE_NSJAIL", "true").lower() not in {"0", "false", "no"}

