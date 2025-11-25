import json
import logging
import os
import subprocess
import secrets
import shutil
import getpass
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


logger = logging.getLogger(__name__)


def _current_user() -> str:
    """
    Return the best-effort name of the OS user running the service.
    """
    try:
        return getpass.getuser()
    except Exception:
        return os.getenv("USER", "unknown")


def _create_workspace() -> Path:
    """
    Create a unique /tmp/nsjail_exec/run_<id>/ directory for a single request.
    """
    Config.SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
    for _ in range(5):
        run_id = secrets.token_hex(8)
        candidate = Config.SANDBOX_ROOT / f"run_{run_id}"
        try:
            candidate.mkdir(mode=0o700)
            return candidate
        except FileExistsError:
            continue
    raise ScriptExecutionError("Unable to allocate sandbox workspace")


def run_script(script: str, timeout: int | None = None) -> Tuple[Any, str]:
    """
    Execute a Python script and return the result and stdout.
    
    Args:
        script: Python script code that defines a main() function
        timeout: Maximum execution time in seconds (default: Config.DEFAULT_TIMEOUT)
        
    Returns:
        tuple: (result, stdout) where result is the return value of main()
        
    Raises:
        MissingMainError: If script doesn't define a callable main()
        InvalidReturnTypeError: If main() returns non-JSON serializable value
        ScriptTimeoutError: If script execution exceeds timeout
        ScriptExecutionError: If script execution fails
    """
    if timeout is None:
        timeout = Config.DEFAULT_TIMEOUT
    
    sandbox_dir: Path | None = None
    try:
        sandbox_dir = _create_workspace()
        logger.info(
            "Starting sandbox %s as user=%s",
            sandbox_dir.name,
            _current_user(),
        )
        script_host_path = sandbox_dir / "user_script.py"
        result_host_path = sandbox_dir / "result.json"
        wrapper_host_path = sandbox_dir / "wrapper.py"
        wrapper_source = (Path(__file__).resolve().parent / "wrapper.py")
        shutil.copy2(wrapper_source, wrapper_host_path)

        # Write user script inside the sandbox mount
        with open(script_host_path, "w") as f:
            f.write(script)

        # nsjail runs without extra namespaces; it only enforces rlimits/env cleanup.
        cmd = [
            "nsjail",
            "--config",
            Config.NSJAIL_CONFIG_PATH,
            "--cwd",
            str(sandbox_dir),
            "--disable_rlimits",
        ]
        cmd.extend([
            "--",
            "/usr/local/bin/python3",
            "wrapper.py",
            str(script_host_path),
            str(result_host_path),
        ])
        command_cwd = str(Config.SANDBOX_ROOT)
        
        # Run nsjail
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=command_cwd,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "Sandbox %s hit timeout=%ss for user=%s",
                sandbox_dir.name if sandbox_dir else "unknown",
                timeout,
                _current_user(),
            )
            raise ScriptTimeoutError(f"Script execution exceeded {timeout} seconds")
        
        stdout_text = result.stdout
        stderr_text = result.stderr
        logger.info(
            "Sandbox %s finished with returncode=%s (stdout_len=%d, stderr_len=%d)",
            sandbox_dir.name,
            result.returncode,
            len(stdout_text or ""),
            len(stderr_text or ""),
        )
        
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
        # Clean up individual sandbox directory only
        if sandbox_dir and sandbox_dir.exists():
            shutil.rmtree(sandbox_dir, ignore_errors=True)
