"""Tests for orchestrator."""

import pytest
import asyncio
from agentforge.core.orchestrator import Orchestrator, OrchestrationConfig
from agentforge.llm.mock_provider import MockLLMProvider


@pytest.fixture
def orchestrator():
    """Create orchestrator."""
    llm = MockLLMProvider()
    return Orchestrator(llm_provider=llm)


@pytest.mark.asyncio
async def test_orchestrator_creation(orchestrator):
    """Test orchestrator creation."""
    assert orchestrator is not None
    assert orchestrator.llm_provider is not None
    assert len(orchestrator.agents) == 0


@pytest.mark.asyncio
async def test_execute_simple_task(orchestrator):
    """Test executing a simple task."""
    result = await orchestrator.execute_task(
        task_description="Write a function that adds two numbers",
        max_iterations=5,
    )

    assert result is not None
    assert result.task_id is not None


@pytest.mark.asyncio
async def test_orchestrator_with_config():
    """Test orchestrator with custom config."""
    config = OrchestrationConfig(
        max_parallel_tasks=2,
        enable_reflection=False,
        enable_caching=False,
    )

    llm = MockLLMProvider()
    orchestrator = Orchestrator(llm_provider=llm, config=config)

    assert orchestrator.config.max_parallel_tasks == 2
    assert orchestrator.config.enable_reflection is False


@pytest.mark.asyncio
async def test_orchestrator_parallel_execution(orchestrator):
    """Test parallel task execution."""
    tasks = [
        "Write FizzBuzz",
        "Write palindrome checker",
        "Write fibonacci",
    ]

    results = await orchestrator.execute_tasks_parallel(tasks)

    assert len(results) == len(tasks)
    for result in results:
        assert result is not None


def test_orchestrator_stats(orchestrator):
    """Test orchestrator statistics."""
    stats = orchestrator.get_stats()

    assert "num_agents" in stats
    assert "cache_size" in stats
    assert "shared_memory_entries" in stats
