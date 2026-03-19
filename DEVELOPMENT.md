# AgentForge Development Guide

Guide for contributing to and extending AgentForge.

## Project Structure

```
agentforge/
├── agentforge/              # Main package
│   ├── core/               # Core orchestration
│   │   ├── agent.py        # Base Agent class
│   │   ├── orchestrator.py # Multi-agent coordinator
│   │   ├── task.py         # Task definitions
│   │   ├── memory.py       # Shared memory system
│   │   └── message.py      # Inter-agent communication
│   │
│   ├── agents/             # Specialized agents
│   │   ├── coder.py        # Code generation
│   │   ├── planner.py      # Task decomposition
│   │   ├── reviewer.py     # Code review
│   │   ├── researcher.py   # Information gathering
│   │   ├── executor.py     # Code execution
│   │   └── verifier.py     # Result verification
│   │
│   ├── reasoning/          # Reasoning strategies
│   │   ├── chain_of_thought.py
│   │   ├── react.py        # Reasoning + Acting
│   │   ├── tree_of_thought.py
│   │   └── reflection.py
│   │
│   ├── tools/              # Agent tools
│   │   ├── code_executor.py
│   │   ├── file_manager.py
│   │   ├── web_search.py
│   │   ├── shell_executor.py
│   │   ├── calculator.py
│   │   └── tool_registry.py
│   │
│   ├── llm/                # LLM providers
│   │   ├── base.py         # Abstract base
│   │   ├── mock_provider.py
│   │   ├── ollama_provider.py
│   │   ├── huggingface_provider.py
│   │   └── openai_provider.py
│   │
│   ├── evaluation/         # Benchmarking
│   │   └── benchmark.py
│   │
│   └── utils/              # Utilities
│       ├── logging.py
│       ├── config.py
│       └── sandbox.py
│
├── examples/               # Example scripts
├── benchmarks/            # Benchmark problems
├── tests/                 # Unit tests
└── docs/                  # Documentation
```

## Adding a New Agent

Create a new agent by extending the `Agent` class:

```python
# agentforge/agents/my_agent.py
from agentforge.core.agent import Agent, ToolDefinition
from typing import Any

class MyAgent(Agent):
    """My specialized agent."""

    def __init__(self, llm_provider: Any):
        tools = [
            ToolDefinition(
                name="my_tool",
                description="Does something useful",
                func=my_tool_function,
                parameters={"input": {"type": "string"}}
            )
        ]

        super().__init__(
            name="my_agent",
            role="My agent's role",
            llm_provider=llm_provider,
            tools=tools,
            system_prompt="You are my agent..."
        )

    async def my_method(self, input_data: str) -> str:
        """Example method."""
        task = Task(description=f"Do something with {input_data}")
        result = await self.think_and_act(task)
        return result.output
```

## Adding a New Tool

Register tools with the decorator:

```python
# agentforge/tools/my_tool.py
from agentforge.tools.tool_registry import ToolRegistry

@ToolRegistry.register(
    name="my_tool",
    description="My custom tool",
    parameters={
        "input": {"type": "string", "description": "Input text"},
        "count": {"type": "integer", "description": "Count"}
    }
)
def my_tool(input: str, count: int = 1) -> str:
    """Execute my tool."""
    return f"{input} * {count}"

# Or use as a tool for an agent:
tool_def = ToolDefinition(
    name="my_tool",
    description="My tool",
    func=my_tool,
    parameters={...}
)
agent.add_tool(tool_def)
```

## Adding a New LLM Provider

Create a new LLM provider:

```python
# agentforge/llm/my_provider.py
from agentforge.llm.base import BaseLLMProvider
from typing import Any, Dict, List, Optional

class MyLLMProvider(BaseLLMProvider):
    """My LLM provider."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize your provider

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response."""
        # Implement generation logic
        return {
            "response": "Generated text",
            "thinking": "Optional reasoning",
            "done": True,
            "tool_calls": []
        }
```

## Adding a New Reasoning Strategy

Create a new reasoning strategy:

```python
# agentforge/reasoning/my_strategy.py
from typing import Any, Dict, List, Optional

class MyReasoner:
    """My reasoning strategy."""

    def __init__(self, llm_provider: Any):
        self.llm_provider = llm_provider

    async def reason(self, problem: str) -> Dict[str, Any]:
        """Solve problem with my strategy."""
        # Implement reasoning logic
        return {
            "answer": "Solution",
            "reasoning_trace": ["step 1", "step 2"],
            "confidence": 0.95
        }
```

## Writing Tests

Create tests in the `tests/` directory:

```python
# tests/test_my_feature.py
import pytest
from agentforge.agents.my_agent import MyAgent
from agentforge.llm.mock_provider import MockLLMProvider

@pytest.fixture
def my_agent():
    llm = MockLLMProvider()
    return MyAgent(llm)

@pytest.mark.asyncio
async def test_my_agent(my_agent):
    result = await my_agent.my_method("test input")
    assert result is not None
    assert len(result) > 0
```

Run tests:

```bash
pytest tests/test_my_feature.py -v
pytest tests/ --cov=agentforge
```

## Code Style

Follow these style guidelines:

1. **Type hints** - Always use type hints

```python
def my_function(x: int, y: str) -> bool:
    """Function with type hints."""
    return True
```

2. **Docstrings** - Use Google-style docstrings

```python
def my_function(x: int) -> str:
    """Short description.

    Longer description if needed.

    Args:
        x: Input value

    Returns:
        Result string

    Raises:
        ValueError: If x is negative
    """
    pass
```

3. **Formatting** - Use black and isort

```bash
black agentforge/
isort agentforge/
```

4. **Linting** - Check with flake8

```bash
flake8 agentforge/
```

## Performance Optimization

### For LLM Calls
- Cache results for repeated queries
- Use smaller models when possible
- Batch multiple requests

### For Code Execution
- Use timeouts to prevent hanging
- Run in isolated subprocesses
- Profile hot paths

### For Memory
- Implement memory eviction policies
- Use relevant similarity for retrieval
- Clear unused entries

## Debugging

Enable debug logging:

```python
import logging
from agentforge.utils.logging import setup_logging

setup_logging(level="DEBUG")
```

Use breakpoints:

```python
import pdb; pdb.set_trace()
```

Use the mock provider for testing:

```python
from agentforge.llm.mock_provider import MockLLMProvider
llm = MockLLMProvider()  # No model needed
```

## Adding Documentation

- Update `README.md` for user-facing features
- Add docstrings to all public methods
- Create examples in `examples/` directory
- Update this guide for developer features

## Release Checklist

Before releasing a new version:

- [ ] Update version in `setup.py`
- [ ] Run all tests: `pytest tests/`
- [ ] Check linting: `flake8 agentforge/`
- [ ] Run benchmarks: `python benchmarks/run_benchmark.py`
- [ ] Update `README.md` if needed
- [ ] Update `CHANGELOG.md`
- [ ] Create git tag: `git tag v0.2.0`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Write tests for new features
5. Run tests: `pytest tests/`
6. Format code: `black agentforge/`
7. Create a pull request

## Common Tasks

### Run all tests
```bash
pytest tests/ -v
```

### Run benchmarks
```bash
python benchmarks/run_benchmark.py
```

### Run examples
```bash
python examples/01_simple_task.py
```

### Format code
```bash
black agentforge/
isort agentforge/
```

### Check types
```bash
mypy agentforge/
```

### Build documentation
```bash
# Documentation generation (if applicable)
```

## Troubleshooting Development

### Import errors
```bash
pip install -e .  # Install in editable mode
```

### Tests failing
```bash
pytest tests/ -vv  # Verbose output
pytest tests/test_file.py::test_function -vv  # Single test
```

### Memory issues
```bash
# Use mock provider to avoid loading models
export AGENTFORGE_LLM_PROVIDER=mock
```

## Architecture Decisions

### Why async/await?
- Enables concurrent agent execution
- Better resource utilization
- Supports long-running tasks

### Why shared memory?
- Agents can share information
- Context between turns
- Learning from history

### Why tool registry?
- Dynamic tool discovery
- Easy extensibility
- Clean interface

## Future Enhancements

- [ ] Multi-modal support (images, audio)
- [ ] Persistent memory across sessions
- [ ] Fine-tuning on custom tasks
- [ ] Distributed execution
- [ ] Web UI for agent monitoring
- [ ] Advanced caching strategies
- [ ] Streaming responses
- [ ] Agent composition/hierarchies

## Resources

- Architecture Paper: (link if available)
- LLM Documentation: https://docs.openai.com/
- Ollama: https://ollama.ai
- HuggingFace: https://huggingface.co/

---

