"""Code execution sandbox utilities."""

import subprocess
import sys
import os
from typing import Optional


class Sandbox:
    """Sandbox for safe code execution."""

    # Blocked imports and operations
    BLOCKED_PATTERNS = [
        "os.system",
        "os.exec",
        "os.environ",
        "subprocess.Popen",
        "subprocess.run",
        "__import__",
        "eval",
        "exec",
        "open",
    ]

    @staticmethod
    def is_safe(code: str) -> bool:
        """Check if code is safe to execute.

        Args:
            code: Code to check

        Returns:
            True if safe
        """
        for pattern in Sandbox.BLOCKED_PATTERNS:
            if pattern in code:
                return False
        return True

    @staticmethod
    def execute(code: str, timeout: int = 30) -> tuple[bool, str]:
        """Execute code safely.

        Args:
            code: Code to execute
            timeout: Timeout in seconds

        Returns:
            (success, output)
        """
        if not Sandbox.is_safe(code):
            return False, "Code contains unsafe operations"

        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                return False, result.stderr or result.stdout

            return True, result.stdout

        except subprocess.TimeoutExpired:
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            return False, str(e)
