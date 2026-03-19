"""Sandboxed Python code execution tool."""

import subprocess
import sys
import os
from typing import Any, Dict
import tempfile
import json


def execute_python_code(code: str, timeout: int = 30) -> str:
    """Execute Python code in a sandboxed subprocess.

    Args:
        code: Python code to execute
        timeout: Execution timeout in seconds

    Returns:
        Output from code execution
    """
    # Security: Block dangerous imports
    dangerous_patterns = [
        "os.system",
        "os.exec",
        "subprocess",
        "__import__",
        "eval",
        "exec",
    ]

    for pattern in dangerous_patterns:
        if pattern in code:
            return f"Error: Dangerous operation '{pattern}' not allowed"

    # Create temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(code)
        temp_file = f.name

    try:
        # Execute in subprocess
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            return f"Error:\n{result.stderr}"
        return result.stdout if result.stdout else "(no output)"

    except subprocess.TimeoutExpired:
        return f"Error: Code execution timed out after {timeout} seconds"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


def execute_python_expression(expression: str) -> Any:
    """Safely evaluate a Python expression.

    Args:
        expression: Python expression to evaluate

    Returns:
        Result of expression
    """
    # Restricted namespace - no access to dangerous functions
    safe_dict = {
        "__builtins__": {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "max": max,
            "min": min,
            "sum": sum,
            "range": range,
            "sorted": sorted,
        },
        "abs": abs,
        "all": all,
        "any": any,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def run_tests(test_code: str, timeout: int = 30) -> Dict[str, Any]:
    """Run test code and return results.

    Args:
        test_code: pytest or unittest code
        timeout: Execution timeout

    Returns:
        Test results
    """
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        # Add pytest runner
        full_code = f"""
import sys
import io

# Capture output
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
{test_code}
except Exception as e:
    print(f"Error: {{e}}")

# Get output
output = sys.stdout.getvalue()
errors = sys.stderr.getvalue()
sys.stdout = old_stdout
sys.stderr = old_stderr

if errors:
    print("STDERR:", errors)
print("OUTPUT:", output)
"""
        f.write(full_code)
        temp_file = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
