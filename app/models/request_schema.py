from pydantic import BaseModel, Field
from app.config import Config

class ScriptRequest(BaseModel):
    script: str = Field(
        ...,
        min_length=1,
        max_length=Config.MAX_SCRIPT_LENGTH,
        description="Python script that defines a main() function",
    )
    timeout: int = Field(
        default=Config.DEFAULT_TIMEOUT,
        ge=1,
        le=300,
        description="Maximum execution time in seconds (1-300)",
    )

