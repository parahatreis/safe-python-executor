from flask import Blueprint, jsonify

from app.models.request_schema import ScriptRequest
from app.models.response_schema import ExecuteSuccessResponse, ExecuteErrorResponse, ErrorInfo
from app.api.middleware import validate_request
from app.execution.executor import run_script
from app.errors.exceptions import (
    MissingMainError,
    InvalidReturnTypeError,
    ScriptTimeoutError,
    ScriptExecutionError,
)

bp = Blueprint("api", __name__)

@bp.route("/")
def hello():
    return {'message': 'Hello, World!'}

@bp.route("/health")
def health():
    return {'status': 'healthy'}

@bp.route("/execute", methods=["POST"])
@validate_request(ScriptRequest)
def execute(payload: ScriptRequest):
    # Execute script via executor
    try:
        result, stdout = run_script(payload.script, timeout=payload.timeout)
    except MissingMainError as e:
        error = ExecuteErrorResponse(
            error=ErrorInfo(
                type="MissingMain",
                message=str(e) or "Script must define a callable main() function",
            )
        )
        return jsonify(error.model_dump()), 400
    except InvalidReturnTypeError as e:
        error = ExecuteErrorResponse(
            error=ErrorInfo(
                type="InvalidReturnType",
                message=str(e) or "main() must return a JSON serializable value",
            )
        )
        return jsonify(error.model_dump()), 400
    except ScriptTimeoutError as e:
        error = ExecuteErrorResponse(
            error=ErrorInfo(
                type="Timeout",
                message=str(e) or "Script execution timed out",
            )
        )
        return jsonify(error.model_dump()), 408
    except ScriptExecutionError as e:
        error = ExecuteErrorResponse(
            error=ErrorInfo(
                type="ScriptExecutionError",
                message=str(e) or "Script failed during execution",
            )
        )
        return jsonify(error.model_dump()), 500

    # 5. Success
    resp = ExecuteSuccessResponse(result=result, stdout=stdout)
    return jsonify(resp.model_dump()), 200
