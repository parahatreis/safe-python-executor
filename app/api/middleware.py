from functools import wraps
from typing import Type, TypeVar

from flask import request, jsonify
from pydantic import BaseModel, ValidationError

from app.models.response_schema import ExecuteErrorResponse, ErrorInfo

T = TypeVar("T", bound=BaseModel)

def validate_request(schema: Type[T]):
    """
    Middleware decorator to validate request body with Pydantic schema.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Check content type
            if not request.is_json:
                error = ExecuteErrorResponse(
                    error=ErrorInfo(
                        type="InvalidContentType",
                        message="Request must be application/json",
                    )
                )
                return jsonify(error.model_dump()), 400

            # 2. Parse JSON body
            try:
                data = request.get_json()
            except Exception:
                error = ExecuteErrorResponse(
                    error=ErrorInfo(
                        type="InvalidJSON",
                        message="Request body must be valid JSON",
                    )
                )
                return jsonify(error.model_dump()), 400

            # 3. Validate payload with Pydantic
            try:
                payload = schema(**data)
            except ValidationError as ve:
                # Extract detailed validation errors
                error_messages = []
                for err in ve.errors():
                    field = ".".join(str(loc) for loc in err["loc"])
                    msg = err["msg"]
                    error_messages.append(f"{field}: {msg}")
                
                error_message = "; ".join(error_messages) if error_messages else "Invalid request payload"
                error = ExecuteErrorResponse(
                    error=ErrorInfo(
                        type="ValidationError",
                        message=error_message,
                    )
                )
                return jsonify(error.model_dump()), 400

            # Pass validated payload to the route handler
            return func(payload, *args, **kwargs)
        
        return wrapper
    return decorator

