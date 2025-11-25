from pydantic import BaseModel, Field

class ScriptRequest(BaseModel):
    script: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="Python script that defines a main() function",
    )

