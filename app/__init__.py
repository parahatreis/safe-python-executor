import logging
import os

from flask import Flask


def configure_logging() -> None:
    """Initialize root logging so INFO logs reach Docker/Gunicorn output."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    else:
        root_logger.setLevel(level)


configure_logging()

app = Flask(__name__)

# Set resource limits
from app.config import Config
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

from app.api.routes import bp as api_bp

app.register_blueprint(api_bp)
