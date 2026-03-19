"""Safe shell command execution."""

import subprocess
import shlex
from typing import Dict, Any


# Whitelist of allowed commands
ALLOWED_COMMANDS = {
    "ls",
    "cat",
    "grep",
    "find",
    "wc",
    "head",
    "tail",
    "echo",
    "pwd",
    "mkdir",
    "touch",
    "rm",
    "cp",
    "mv",
    "sort",
    "uniq",
    "cut",
    "tr",
    "sed",
    "awk",
}


def execute_shell_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute a whitelisted shell command safely.

    Args:
        command: Shell command
        timeout: Execution timeout in seconds

    Returns:
        Command result
    """
    # Parse command
    try:
        parts = shlex.split(command)
    except:
        return {
            "success": False,
            "error": "Invalid command syntax",
        }

    if not parts:
        return {"success": False, "error": "Empty command"}

    # Check if command is allowed
    cmd_name = parts[0]
    if cmd_name not in ALLOWED_COMMANDS:
        return {
            "success": False,
            "error": f"Command '{cmd_name}' not allowed. Allowed: {', '.join(sorted(ALLOWED_COMMANDS))}",
        }

    # Execute
    try:
        result = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def list_directory(path: str = ".") -> str:
    """List files in a directory.

    Args:
        path: Directory path

    Returns:
        Formatted file listing
    """
    result = execute_shell_command(f"ls -lah {path}")

    if result["success"]:
        return result["stdout"]
    return result["error"]


def search_text(file_path: str, pattern: str) -> str:
    """Search for text in a file.

    Args:
        file_path: File to search
        pattern: Search pattern

    Returns:
        Matching lines
    """
    result = execute_shell_command(f"grep -n '{pattern}' {file_path}")

    if result["success"]:
        return result["stdout"] if result["stdout"] else "No matches found"
    return result["error"]
