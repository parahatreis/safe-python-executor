class ScriptExecutionError(Exception):
    """Generic error when running the script."""

class MissingMainError(ScriptExecutionError):
    """Raised when script does not define a callable main()."""

class InvalidReturnTypeError(ScriptExecutionError):
    """Raised when main() returns a non JSON serializable value."""

class ScriptTimeoutError(ScriptExecutionError):
    """Raised when script execution exceeds the allowed time."""

