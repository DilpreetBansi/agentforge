#!/usr/bin/env python3
"""
Example 3: Specialized Agents
Shows how to use specific agents: Coder, Reviewer, Researcher
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge.agents.coder import CoderAgent
from agentforge.agents.reviewer import ReviewerAgent
from agentforge.agents.planner import PlannerAgent
from agentforge.llm.mock_provider import MockLLMProvider


async def main():
    """Run specialized agents example."""
    print("=" * 70)
    print("AgentForge Example 3: Specialized Agents")
    print("=" * 70)
    print()

    # Create LLM provider
    llm = MockLLMProvider()
    print("✓ Initialized MockLLMProvider")
    print()

    # Example 1: Coder Agent
    print("=" * 70)
    print("1. CODER AGENT - Code Generation")
    print("=" * 70)

    coder = CoderAgent(llm_provider=llm)
    spec = "Write a function that checks if a number is a palindrome"
    print(f"Specification: {spec}")
    print()

    code = coder.generate_code(spec)
    print("Generated Code:")
    print("-" * 70)
    print(code[:400])
    if len(code) > 400:
        print("...")
    print("-" * 70)
    print()

    # Example 2: Reviewer Agent
    print("=" * 70)
    print("2. REVIEWER AGENT - Code Review")
    print("=" * 70)

    reviewer = ReviewerAgent(llm_provider=llm)
    review = reviewer.review_code(code, spec)

    print("Code Review Results:")
    print("-" * 70)
    if isinstance(review, dict):
        print(f"Quality Score: {review.get('quality_score', 'N/A')}/100")
        print(f"Recommendation: {review.get('recommendation', 'N/A')}")
        if review.get("issues"):
            print("Issues found:")
            for issue in review["issues"][:2]:
                print(f"  - [{issue.get('severity')}] {issue.get('description')}")
    else:
        print(review[:300])
    print("-" * 70)
    print()

    # Example 3: Planner Agent
    print("=" * 70)
    print("3. PLANNER AGENT - Task Decomposition")
    print("=" * 70)

    planner = PlannerAgent(llm_provider=llm)
    complex_task = "Build a web scraper that fetches product data and saves to database"
    print(f"Complex Task: {complex_task}")
    print()

    plan = planner.decompose_task(complex_task)
    print("Decomposition Plan:")
    print("-" * 70)

    if isinstance(plan, dict) and "subtasks" in plan:
        for i, subtask in enumerate(plan["subtasks"][:3], 1):
            print(f"{i}. {subtask.get('description', 'N/A')}")
            print(f"   Agent: {subtask.get('agent', 'N/A')}")
            print(f"   Difficulty: {subtask.get('difficulty', 'N/A')}")
    else:
        print(json.dumps(plan, indent=2)[:500])

    print("-" * 70)
    print()

    # Example 4: Complexity Estimation
    print("=" * 70)
    print("4. COMPLEXITY ESTIMATION")
    print("=" * 70)

    complexity = planner.estimate_complexity(complex_task)
    print(f"Task: {complex_task}")
    print()
    print("Complexity Analysis:")
    print(f"  Difficulty: {complexity.get('difficulty', 'N/A')}")
    print(f"  Estimated Iterations: {complexity.get('estimated_iterations', 'N/A')}")
    if complexity.get("required_tools"):
        print(f"  Required Tools: {', '.join(complexity['required_tools'][:3])}")
    print()

    print("✓ Specialized agents example completed!")


if __name__ == "__main__":
    asyncio.run(main())
