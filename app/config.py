import os
from pathlib import Path


class Config:
    """Application configuration."""
    
    # Paths
    NSJAIL_CONFIG_PATH = str(Path(__file__).parent / "execution" / "nsjail_config.cfg")
    SANDBOX_ROOT = Path(os.getenv("SANDBOX_ROOT", "/tmp/nsjail_exec"))
    
    # Execution settings
    NSJAIL_ENABLED = os.getenv("ENABLE_NSJAIL", "true").lower() not in {"0", "false", "no"}
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    MAX_SCRIPT_LENGTH = int(os.getenv("MAX_SCRIPT_LENGTH", "20000"))
    
    # Resource limits
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "20971520"))  # 20MB default

