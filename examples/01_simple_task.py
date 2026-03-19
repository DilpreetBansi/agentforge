#!/usr/bin/env python3
"""
Example 1: Simple Task with Mock Provider
No model required - works immediately!
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge.core.agent import Agent
from agentforge.llm.mock_provider import MockLLMProvider
from agentforge.core.task import Task


async def main():
    """Run simple task example."""
    print("=" * 60)
    print("AgentForge Example 1: Simple Task (Mock Provider)")
    print("=" * 60)
    print()

    # Create LLM provider (mock - no model needed!)
    llm = MockLLMProvider()
    print("✓ Initialized MockLLMProvider (no model required)")
    print()

    # Create a simple agent
    agent = Agent(
        name="code_assistant",
        role="Python programming assistant",
        llm_provider=llm,
        system_prompt="You are a helpful Python programming assistant. Write clean, well-tested code.",
    )
    print(f"✓ Created agent: {agent.name}")
    print()

    # Define a task
    task = Task(
        description="Write a Python function that returns the sum of two numbers",
        constraints=["Function must have docstring", "Must handle edge cases"],
        max_iterations=5,
    )
    print(f"Task: {task.description}")
    print()

    # Solve the task
    print("Solving task...")
    print("-" * 60)
    result = await agent.think_and_act(task)
    print("-" * 60)
    print()

    # Display results
    print("RESULTS")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Iterations: {result.metrics.get('iterations', 0)}")
    print()
    print("Output:")
    print("-" * 60)
    print(result.output)
    print("-" * 60)
    print()

    if result.reasoning_trace:
        print("Reasoning trace:")
        for i, step in enumerate(result.reasoning_trace[-3:], 1):
            print(f"  {i}. {step[:80]}...")
    print()

    print("✓ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
