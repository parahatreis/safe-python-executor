from pathlib import Path


class Config:
    """Application configuration."""
    
    NSJAIL_CONFIG_PATH = str(Path(__file__).parent / "execution" / "nsjail_config.cfg")

