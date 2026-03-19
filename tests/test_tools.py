"""Tests for tool implementations."""

import pytest
import tempfile
import os
from agentforge.tools.code_executor import execute_python_code, execute_python_expression
from agentforge.tools.file_manager import read_file, write_file, delete_file, list_files
from agentforge.tools.calculator import evaluate_expression, solve_quadratic
from agentforge.tools.shell_executor import execute_shell_command


def test_code_executor():
    """Test code execution."""
    code = """
result = 2 + 2
print(result)
"""
    output = execute_python_code(code)
    assert "4" in output


def test_dangerous_code_blocked():
    """Test that dangerous code is blocked."""
    code = "import os; os.system('echo hack')"
    output = execute_python_code(code)
    assert "not allowed" in output.lower()


def test_code_timeout():
    """Test code execution timeout."""
    code = """
import time
while True:
    time.sleep(1)
"""
    output = execute_python_code(code, timeout=1)
    assert "timeout" in output.lower()


def test_expression_evaluation():
    """Test safe expression evaluation."""
    result = execute_python_expression("2 + 3 * 4")
    assert result == 14


def test_file_operations():
    """Test file read/write operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.txt")
        content = "Hello, World!"

        # Write
        result = write_file(filepath, content)
        assert "Successfully wrote" in result

        # Read
        read_result = read_file(filepath)
        assert read_result == content

        # Delete
        delete_result = delete_file(filepath)
        assert "Successfully deleted" in delete_result


def test_list_files():
    """Test file listing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        open(os.path.join(tmpdir, "file1.py"), "w").close()
        open(os.path.join(tmpdir, "file2.py"), "w").close()

        # List files
        files = list_files(tmpdir)
        assert len(files) >= 2


def test_quadratic_solver():
    """Test quadratic equation solver."""
    # x^2 - 5x + 6 = 0, solutions are x=2 and x=3
    result = solve_quadratic(1, -5, 6)

    assert "x1" in result
    assert "x2" in result
    assert abs(result["x1"] - 3.0) < 0.01 or abs(result["x1"] - 2.0) < 0.01


def test_shell_command_allowed():
    """Test whitelisted shell commands."""
    result = execute_shell_command("echo hello")
    assert result["success"]
    assert "hello" in result["stdout"]


def test_shell_command_blocked():
    """Test blocked shell commands."""
    result = execute_shell_command("python -c 'import os; os.system(\"id\")'")
    assert not result["success"]
    assert "not allowed" in result["error"].lower()


def test_calculator():
    """Test calculator tool."""
    result = evaluate_expression("sqrt(16)")
    assert result == 4.0

    result = evaluate_expression("sin(pi/2)")
    assert abs(result - 1.0) < 0.01
