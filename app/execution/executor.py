import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Any, Tuple

from app.config import Config
from app.errors.exceptions import (
    MissingMainError,
    InvalidReturnTypeError,
    ScriptTimeoutError,
    ScriptExecutionError,
)
from app.execution.wrapper import (
    EXIT_OK,
    EXIT_MISSING_MAIN,
    EXIT_INVALID_RETURN,
    EXIT_RUNTIME_ERROR,
)


SANDBOX_ROOT = Path("/tmp/nsjail_exec")


def run_script(script: str, timeout: int = 30) -> Tuple[Any, str]:
    """
    Execute a Python script and return the result and stdout.
    
    Args:
        script: Python script code that defines a main() function
        timeout: Maximum execution time in seconds (default: 30)
        
    Returns:
        tuple: (result, stdout) where result is the return value of main()
        
    Raises:
        MissingMainError: If script doesn't define a callable main()
        InvalidReturnTypeError: If main() returns non-JSON serializable value
        ScriptTimeoutError: If script execution exceeds timeout
        ScriptExecutionError: If script execution fails
    """
    sandbox_dir: Path | None = None
    try:
        SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
        sandbox_dir = Path(
            tempfile.mkdtemp(prefix="run_", dir=str(SANDBOX_ROOT))
        )
        sandbox_name = sandbox_dir.name
        script_host_path = sandbox_dir / "user_script.py"
        result_host_path = sandbox_dir / "result.json"

        # Write user script inside the sandbox mount
        with open(script_host_path, "w") as f:
            f.write(script)

        wrapper_path = (
            Path(__file__)
            .resolve()
            .parent
            / "wrapper.py"
        )
        wrapper_path = wrapper_path.resolve()

        script_jail_path = f"/tmp/{sandbox_name}/user_script.py"
        result_jail_path = f"/tmp/{sandbox_name}/result.json"
        
        # Build nsjail command
        # Use absolute path to python3
        nsjail_cmd = [
            "nsjail",
            "--config", Config.NSJAIL_CONFIG_PATH,
            "--",
            "/usr/local/bin/python3",
            "/wrapper.py",
            script_jail_path,
            result_jail_path,
        ]
        
        # Run nsjail
        try:
            result = subprocess.run(
                nsjail_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=wrapper_path.parent,
            )
        except subprocess.TimeoutExpired:
            raise ScriptTimeoutError(f"Script execution exceeded {timeout} seconds")
        
        stdout_text = result.stdout
        stderr_text = result.stderr
        
        # Map exit codes to exceptions
        if result.returncode == EXIT_MISSING_MAIN:
            raise MissingMainError("Script must define a callable main() function")
        elif result.returncode == EXIT_INVALID_RETURN:
            raise InvalidReturnTypeError("main() must return a JSON serializable value")
        elif result.returncode == EXIT_RUNTIME_ERROR:
            error_msg = stderr_text or "Script failed during execution"
            raise ScriptExecutionError(error_msg)
        elif result.returncode != EXIT_OK:
            error_msg = stderr_text or f"Script execution failed with exit code {result.returncode}"
            raise ScriptExecutionError(error_msg)
        
        # Read result.json
        if not result_host_path.exists():
            raise ScriptExecutionError("Result file was not created")
        
        with open(result_host_path, "r") as f:
            result_data = json.load(f)
        
        return result_data, stdout_text
        
    finally:
        if sandbox_dir and sandbox_dir.exists():
            shutil.rmtree(sandbox_dir, ignore_errors=True)
        try:
            SANDBOX_ROOT.rmdir()
        except OSError:
            pass
