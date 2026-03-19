"""Mathematical computation tool."""

import math
from typing import Union, Any


def evaluate_expression(expression: str) -> Union[float, str]:
    """Safely evaluate a mathematical expression.

    Args:
        expression: Mathematical expression

    Returns:
        Result or error message
    """
    # Safe namespace with math functions
    safe_dict = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "pi": math.pi,
        "e": math.e,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def solve_quadratic(a: float, b: float, c: float) -> dict:
    """Solve quadratic equation ax^2 + bx + c = 0.

    Args:
        a, b, c: Coefficients

    Returns:
        Solutions
    """
    if a == 0:
        if b == 0:
            return {"error": "Not a valid equation"}
        return {"x": -c / b}

    discriminant = b * b - 4 * a * c

    if discriminant < 0:
        return {"error": "No real solutions"}

    sqrt_d = math.sqrt(discriminant)
    x1 = (-b + sqrt_d) / (2 * a)
    x2 = (-b - sqrt_d) / (2 * a)

    return {"x1": x1, "x2": x2, "discriminant": discriminant}


def compute_statistics(numbers: list) -> dict:
    """Compute statistics on a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        Statistics
    """
    if not numbers:
        return {"error": "Empty list"}

    n = len(numbers)
    mean = sum(numbers) / n
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = math.sqrt(variance)

    return {
        "count": n,
        "sum": sum(numbers),
        "mean": mean,
        "median": sorted(numbers)[n // 2],
        "min": min(numbers),
        "max": max(numbers),
        "variance": variance,
        "std_dev": std_dev,
    }
