#!/usr/bin/env python3
"""
Benchmark runner for AgentForge
Evaluates agent performance on coding problems
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge.agents.coder import CoderAgent
from agentforge.llm.mock_provider import MockLLMProvider
from agentforge.tools.code_executor import execute_python_code


class BenchmarkRunner:
    """Runs benchmarks on agent implementations."""

    def __init__(self, provider_type: str = "mock"):
        """Initialize benchmark runner.

        Args:
            provider_type: LLM provider type (mock, ollama, huggingface, openai)
        """
        self.provider_type = provider_type

        # Initialize LLM provider
        if provider_type == "mock":
            self.llm = MockLLMProvider()
        else:
            print(f"Provider '{provider_type}' not yet configured in benchmark runner")
            print("Using mock provider instead")
            self.llm = MockLLMProvider()

        self.results: List[Dict[str, Any]] = []

    async def load_problems(self, problem_dir: str) -> List[Dict[str, Any]]:
        """Load benchmark problems from JSON files.

        Args:
            problem_dir: Directory containing problem JSON files

        Returns:
            List of problem definitions
        """
        problems = []
        problem_path = Path(problem_dir)

        if not problem_path.exists():
            print(f"Problem directory not found: {problem_dir}")
            return problems

        for problem_file in sorted(problem_path.glob("problem_*.json")):
            try:
                with open(problem_file) as f:
                    problem = json.load(f)
                    problems.append(problem)
            except json.JSONDecodeError as e:
                print(f"Error loading {problem_file}: {e}")

        return problems

    async def run_problem(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single benchmark problem.

        Args:
            problem: Problem definition

        Returns:
            Result with metrics
        """
        problem_id = problem.get("id", "unknown")
        title = problem.get("title", "Unknown")
        description = problem.get("description", "")

        print(f"\nRunning: {problem_id} - {title}")
        print(f"  Difficulty: {problem.get('difficulty', 'unknown')}")

        start_time = time.time()

        # Create coder agent
        coder = CoderAgent(llm_provider=self.llm)

        # Generate code
        try:
            code = coder.generate_code(description)

            # Try to execute and test
            test_passed = False
            execution_time = 0

            # Simple test: check if function is defined
            test_start = time.time()
            try:
                exec_result = execute_python_code(code)
                execution_time = time.time() - test_start
                test_passed = "Error" not in exec_result and exec_result != ""
            except:
                execution_time = time.time() - test_start

            elapsed = time.time() - start_time

            result = {
                "problem_id": problem_id,
                "title": title,
                "success": test_passed,
                "elapsed_time": elapsed,
                "code_length": len(code),
                "iterations": 1,
                "difficulty": problem.get("difficulty", "unknown"),
            }

            status = "✓" if test_passed else "✗"
            print(f"  {status} Result: {'PASS' if test_passed else 'FAIL'} ({elapsed:.2f}s)")

            return result

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  ✗ Error: {str(e)[:50]}")
            return {
                "problem_id": problem_id,
                "title": title,
                "success": False,
                "elapsed_time": elapsed,
                "error": str(e),
                "difficulty": problem.get("difficulty", "unknown"),
            }

    async def run_all(
        self, problem_dir: str, filter_problem: str = ""
    ) -> List[Dict[str, Any]]:
        """Run all problems in a directory.

        Args:
            problem_dir: Directory containing problems
            filter_problem: Only run problems matching this ID

        Returns:
            List of results
        """
        problems = await self.load_problems(problem_dir)

        if not problems:
            print("No problems found!")
            return []

        if filter_problem:
            problems = [p for p in problems if filter_problem in p.get("id", "")]

        print(f"Found {len(problems)} problem(s)")
        print("=" * 70)

        results = []
        for problem in problems:
            result = await self.run_problem(problem)
            results.append(result)
            self.results.append(result)

        return results

    def print_summary(self):
        """Print summary statistics."""
        if not self.results:
            print("No results to summarize")
            return

        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)

        # Calculate metrics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success", False))
        failed = total - passed

        avg_time = sum(r.get("elapsed_time", 0) for r in self.results) / total if total > 0 else 0
        total_code_length = sum(r.get("code_length", 0) for r in self.results)

        # Print table
        print(f"\nResults by Difficulty:")
        print("-" * 70)

        difficulties = {}
        for result in self.results:
            diff = result.get("difficulty", "unknown")
            if diff not in difficulties:
                difficulties[diff] = {"total": 0, "passed": 0}
            difficulties[diff]["total"] += 1
            if result.get("success"):
                difficulties[diff]["passed"] += 1

        for diff in sorted(difficulties.keys()):
            stats = difficulties[diff]
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {diff.upper():10s}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")

        print("\nOverall Statistics:")
        print("-" * 70)
        print(f"  Total Problems: {total}")
        print(f"  Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"  Failed: {failed}")
        print(f"  Avg Time per Problem: {avg_time:.2f}s")
        print(f"  Total Code Generated: {total_code_length} chars")
        print(f"  Provider: {self.provider_type}")

        print("\nDetailed Results:")
        print("-" * 70)
        print(f"{'ID':<15} {'Title':<20} {'Status':<8} {'Time':<8}")
        print("-" * 70)

        for result in self.results:
            problem_id = result.get("problem_id", "?")
            title = result.get("title", "?")[:18]
            status = "✓ PASS" if result.get("success") else "✗ FAIL"
            elapsed = result.get("elapsed_time", 0)
            print(f"{problem_id:<15} {title:<20} {status:<8} {elapsed:>6.2f}s")

        print("=" * 70)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AgentForge Benchmark Runner")
    parser.add_argument(
        "--provider",
        default="mock",
        help="LLM provider (mock, ollama, huggingface, openai)",
    )
    parser.add_argument(
        "--problem", default="", help="Run only problems matching this ID"
    )
    parser.add_argument(
        "--dir", default="benchmarks/problems", help="Directory containing problems"
    )

    args = parser.parse_args()

    # Create runner
    runner = BenchmarkRunner(provider_type=args.provider)

    # Get problem directory
    problem_dir = args.dir
    if not os.path.isabs(problem_dir):
        # Make relative to this file
        problem_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), problem_dir
        )

    # Run benchmarks
    await runner.run_all(problem_dir, filter_problem=args.problem)

    # Print summary
    runner.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
