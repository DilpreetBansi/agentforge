"""Evaluation benchmark framework."""

import json
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """Result from a benchmark."""

    problem_id: str
    success: bool
    elapsed_time: float
    reasoning_steps: int
    tokens_used: int = 0
    error: Optional[str] = None


class BenchmarkFramework:
    """Framework for evaluating agents."""

    def __init__(self):
        """Initialize benchmark framework."""
        self.results: List[BenchmarkResult] = []

    def evaluate_solution(
        self, solution: str, test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate a solution against test cases.

        Args:
            solution: Solution code
            test_cases: List of test cases

        Returns:
            Evaluation results
        """
        passed = 0
        failed = 0

        for test in test_cases:
            try:
                # Create test environment
                env = {}
                exec(solution, env)

                # Extract function name (first defined function)
                func_name = None
                for name in env:
                    if callable(env[name]) and not name.startswith("_"):
                        func_name = name
                        break

                if func_name:
                    func = env[func_name]

                    # Run test
                    input_data = test.get("input", {})
                    expected = test.get("expected_output")

                    if isinstance(input_data, dict):
                        result = func(**input_data)
                    else:
                        result = func(input_data)

                    if result == expected:
                        passed += 1
                    else:
                        failed += 1
                else:
                    failed += 1

            except Exception as e:
                failed += 1

        return {
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "success_rate": (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.results:
            return {"total_problems": 0, "success_rate": 0}

        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)

        avg_time = sum(r.elapsed_time for r in self.results) / total
        avg_steps = sum(r.reasoning_steps for r in self.results) / total

        return {
            "total_problems": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total * 100),
            "avg_time_seconds": avg_time,
            "avg_reasoning_steps": avg_steps,
            "total_tokens": sum(r.tokens_used for r in self.results),
        }
