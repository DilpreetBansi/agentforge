"""Tests for agent implementations."""

import pytest
import asyncio
from agentforge.core.agent import Agent
from agentforge.agents.coder import CoderAgent
from agentforge.agents.planner import PlannerAgent
from agentforge.agents.reviewer import ReviewerAgent
from agentforge.llm.mock_provider import MockLLMProvider
from agentforge.core.task import Task


@pytest.fixture
def llm_provider():
    """Create mock LLM provider."""
    return MockLLMProvider()


@pytest.fixture
def simple_agent(llm_provider):
    """Create simple agent."""
    return Agent(
        name="test_agent",
        role="Test agent",
        llm_provider=llm_provider,
    )


@pytest.mark.asyncio
async def test_agent_creation(simple_agent):
    """Test agent creation."""
    assert simple_agent.name == "test_agent"
    assert simple_agent.role == "Test agent"
    assert simple_agent.max_iterations == 20


@pytest.mark.asyncio
async def test_agent_think_and_act(simple_agent):
    """Test agent thinking and acting."""
    task = Task(
        description="Write a simple Python function",
        max_iterations=5,
    )

    result = await simple_agent.think_and_act(task)

    assert result is not None
    assert result.task_id == task.task_id
    assert result.iteration_count > 0


@pytest.mark.asyncio
async def test_coder_agent(llm_provider):
    """Test coder agent."""
    coder = CoderAgent(llm_provider=llm_provider)

    assert coder.name == "coder"
    assert len(coder.tools) > 0


@pytest.mark.asyncio
async def test_planner_agent(llm_provider):
    """Test planner agent."""
    planner = PlannerAgent(llm_provider=llm_provider)

    plan = planner.decompose_task("Build a web scraper")

    assert plan is not None
    if "subtasks" in plan:
        assert len(plan["subtasks"]) > 0


@pytest.mark.asyncio
async def test_reviewer_agent(llm_provider):
    """Test reviewer agent."""
    reviewer = ReviewerAgent(llm_provider=llm_provider)

    code = "def hello():\n    return 'world'"
    review = reviewer.review_code(code)

    assert review is not None
    if isinstance(review, dict):
        assert "quality_score" in review or "assessment" in review


def test_agent_tool_registration(simple_agent):
    """Test tool registration."""
    from agentforge.core.agent import ToolDefinition

    def dummy_tool(x: int) -> int:
        return x * 2

    tool = ToolDefinition(
        name="dummy",
        description="Dummy tool",
        func=dummy_tool,
        parameters={"x": {"type": "integer"}},
    )

    simple_agent.add_tool(tool)

    assert len(simple_agent.tools) == 1
    assert simple_agent.tools[0].name == "dummy"
