#!/usr/bin/env python3
"""
Example 2: Multi-Agent Collaboration
Uses Orchestrator to coordinate multiple agents on a complex task
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge.core.orchestrator import Orchestrator, OrchestrationConfig
from agentforge.llm.mock_provider import MockLLMProvider


async def main():
    """Run multi-agent example."""
    print("=" * 70)
    print("AgentForge Example 2: Multi-Agent Collaboration")
    print("=" * 70)
    print()

    # Create LLM provider
    llm = MockLLMProvider()
    print("✓ Initialized MockLLMProvider")
    print()

    # Create orchestrator with config
    config = OrchestrationConfig(
        max_parallel_tasks=2,
        enable_reflection=True,
        enable_caching=False,
    )
    orchestrator = Orchestrator(llm_provider=llm, config=config)
    print("✓ Created Orchestrator")
    print()

    # Define a complex task
    task_description = """
Build a complete solution for FizzBuzz problem:
1. Plan the approach
2. Implement the code
3. Review the code
4. Verify it works correctly
"""

    print(f"Task: {task_description.strip()}")
    print()

    # Execute task through orchestrator
    print("Executing multi-agent task...")
    print("=" * 70)

    result = await orchestrator.execute_task(
        task_description=task_description,
        context="FizzBuzz: Print 1-100, but print 'Fizz' for multiples of 3, 'Buzz' for multiples of 5",
        constraints=[
            "Must handle all numbers 1-100",
            "Must be efficient",
            "Must be well-tested",
        ],
        max_iterations=15,
    )

    print("=" * 70)
    print()

    # Display results
    print("RESULTS")
    print("=" * 70)
    print(f"Success: {result.success}")
    print(f"Elapsed time: {result.metrics.get('elapsed_time_seconds', 0):.2f}s")
    print(f"Number of agents used: {result.metrics.get('num_agents', 0)}")
    print()

    print("Final Output:")
    print("-" * 70)
    print(result.output[:500] + "..." if len(result.output) > 500 else result.output)
    print("-" * 70)
    print()

    if result.subtask_results:
        print(f"Subtasks completed: {len(result.subtask_results)}")
        for agent_name, subtask_result in list(result.subtask_results.items())[:3]:
            print(f"  - {agent_name}: {'✓' if subtask_result.success else '✗'}")
    print()

    # Orchestrator stats
    stats = orchestrator.get_stats()
    print("Orchestrator Stats:")
    print(f"  - Total agents: {stats['num_agents']}")
    print(f"  - Shared memory entries: {stats['shared_memory_entries']}")
    print(f"  - Cache size: {stats['cache_size']}")
    print()

    print("✓ Multi-agent example completed!")


if __name__ == "__main__":
    asyncio.run(main())
