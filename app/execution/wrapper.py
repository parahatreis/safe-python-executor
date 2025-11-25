#!/usr/bin/env python3
"""
Wrapper script that runs inside nsjail sandbox.
Executes user scripts and handles errors appropriately.
"""
import sys
import json
import traceback
import runpy

# Exit code constants
EXIT_OK = 0
EXIT_MISSING_MAIN = 1
EXIT_INVALID_RETURN = 2
EXIT_RUNTIME_ERROR = 3


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <script_path> <result_path>", file=sys.stderr)
        sys.exit(EXIT_RUNTIME_ERROR)
    
    script_path = sys.argv[1]
    result_path = sys.argv[2]
    
    # Load and execute the script
    try:
        script_globals = runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        print(f"Failed to load script: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(EXIT_RUNTIME_ERROR)
    
    # Check for main function
    if "main" not in script_globals:
        sys.exit(EXIT_MISSING_MAIN)
    
    main_func = script_globals["main"]
    if not callable(main_func):
        sys.exit(EXIT_MISSING_MAIN)
    
    # Call main()
    try:
        result = main_func()
    except Exception as e:
        print(f"Error in main(): {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(EXIT_RUNTIME_ERROR)
    
    # Check if result is JSON serializable
    try:
        json.dumps(result)
    except (TypeError, ValueError) as e:
        print(f"Return value is not JSON serializable: {e}", file=sys.stderr)
        sys.exit(EXIT_INVALID_RETURN)
    
    # Write result to file
    try:
        with open(result_path, "w") as f:
            json.dump(result, f)
    except Exception as e:
        print(f"Failed to write result: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(EXIT_RUNTIME_ERROR)
    
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
