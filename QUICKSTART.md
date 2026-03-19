# AgentForge Quick Start Guide

Get up and running with AgentForge in 5 minutes!

## Installation

```bash
# Clone the repository
cd agentforge

# Install dependencies
pip install -r requirements.txt

# Optional: Install extras for transformers support
pip install transformers torch
```

## Run Your First Example (No Model Required!)

AgentForge includes a **mock LLM provider** that works without any model:

```bash
# Run simple example - works immediately
python examples/01_simple_task.py
```

Expected output:
```
============================================================
AgentForge Example 1: Simple Task (Mock Provider)
============================================================

✓ Initialized MockLLMProvider (no model required)
✓ Created agent: code_assistant

Task: Write a Python function that returns the sum of two numbers

Solving task...
...

RESULTS
============================================================
Success: True
Output:
def add_numbers(a, b):
    '''Return the sum of two numbers.'''
    return a + b
...
```

## Next Examples

Try the other examples in order:

```bash
# Multi-agent coordination
python examples/02_multi_agent.py

# Specialized agents (Coder, Reviewer, Planner)
python examples/03_specialized_agents.py

# Complete code generation pipeline
python examples/04_code_generation_pipeline.py
```

## Run Benchmarks

```bash
# Run all benchmarks
python benchmarks/run_benchmark.py

# Run specific problem
python benchmarks/run_benchmark.py --problem problem_001

# Run with specific provider
python benchmarks/run_benchmark.py --provider mock
```

## Using with Real Models

### Option 1: Ollama (Recommended - Fast, Local)

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model
ollama pull mistral  # or: llama2, codellama, neural-chat, etc.

# 3. Start Ollama server
ollama serve  # Runs on http://localhost:11434

# 4. In another terminal, run with Ollama
python examples/01_simple_task.py --provider ollama
```

### Option 2: HuggingFace Transformers (CPU/GPU)

```bash
# Install transformers
pip install transformers torch

# Set environment variables
export AGENTFORGE_LLM_PROVIDER=huggingface
export AGENTFORGE_HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
export AGENTFORGE_HF_DEVICE=cuda  # or 'cpu'

# Run
python examples/01_simple_task.py
```

### Option 3: OpenAI API

```bash
# Set your API key
export OPENAI_API_KEY=sk-your-key-here

# Run with OpenAI
export AGENTFORGE_LLM_PROVIDER=openai
python examples/01_simple_task.py
```

### Option 4: Compatible API (LM Studio, vLLM)

```bash
# Using LM Studio or vLLM running locally
export AGENTFORGE_LLM_PROVIDER=openai
export OPENAI_API_BASE=http://localhost:8000
export OPENAI_API_KEY=not-needed
python examples/01_simple_task.py
```

## Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=agentforge
```

## Key Features to Try

### 1. Simple Agent

```python
from agentforge.core.agent import Agent
from agentforge.llm.mock_provider import MockLLMProvider
from agentforge.core.task import Task
import asyncio

async def main():
    llm = MockLLMProvider()
    agent = Agent("assistant", "helpful AI", llm)

    task = Task(description="Write a Python function for FizzBuzz")
    result = await agent.think_and_act(task)

    print(result.output)

asyncio.run(main())
```

### 2. Multi-Agent Orchestration

```python
from agentforge.core.orchestrator import Orchestrator
from agentforge.llm.mock_provider import MockLLMProvider
import asyncio

async def main():
    llm = MockLLMProvider()
    orchestrator = Orchestrator(llm)

    result = await orchestrator.execute_task(
        "Write a complete solution for the Two Sum problem"
    )

    print(f"Success: {result.success}")
    print(f"Output: {result.output}")

asyncio.run(main())
```

### 3. Specialized Agents

```python
from agentforge.agents.coder import CoderAgent
from agentforge.agents.reviewer import ReviewerAgent
from agentforge.llm.mock_provider import MockLLMProvider

llm = MockLLMProvider()

# Generate code
coder = CoderAgent(llm)
code = coder.generate_code("Write a palindrome checker")

# Review code
reviewer = ReviewerAgent(llm)
review = reviewer.review_code(code)
print(f"Quality score: {review.get('quality_score', 'N/A')}/100")
```

## Configuration

Create `.env` file:

```bash
# LLM Provider
AGENTFORGE_LLM_PROVIDER=mock  # or: ollama, huggingface, openai

# Ollama
AGENTFORGE_OLLAMA_BASE_URL=http://localhost:11434
AGENTFORGE_OLLAMA_MODEL=mistral

# HuggingFace
AGENTFORGE_HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
AGENTFORGE_HF_DEVICE=cuda

# Agent behavior
AGENTFORGE_MAX_ITERATIONS=20
AGENTFORGE_ENABLE_REFLECTION=true

# Logging
AGENTFORGE_LOG_LEVEL=INFO
```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# Check it's accessible
curl http://localhost:11434/api/tags
```

### Out of Memory
```bash
# Use a smaller model
ollama pull mistral  # Faster than llama2

# Or quantize the model
ollama pull mistral:7b-instruct-q4_0
```

### No GPU Available
```bash
export AGENTFORGE_HF_DEVICE=cpu
# Note: CPU inference will be slower
```

### Tests Failing
```bash
# Make sure dependencies are installed
pip install -r requirements.txt
pip install pytest pytest-asyncio

# Run tests with verbose output
pytest tests/ -vv
```

## Architecture Overview

```
User Task
    ↓
Orchestrator (Coordinates agents)
    ├→ Planner Agent (Decomposes task)
    ├→ Coder Agent (Writes code)
    ├→ Reviewer Agent (Reviews code)
    ├→ Executor Agent (Runs code)
    ├→ Verifier Agent (Validates results)
    └→ Researcher Agent (Gathers info)
    ↓
Shared Memory (Context + History)
    ↓
LLM Provider (Mock / Ollama / HF / OpenAI)
    ↓
Final Result
```

## Next Steps

1. **Read the full README**: See `README.md` for detailed documentation
2. **Explore examples**: Each example shows different capabilities
3. **Check out benchmarks**: See how agents perform on coding problems
4. **Customize agents**: Create your own agents by extending `Agent` class
5. **Add tools**: Register custom tools with the `@register_tool` decorator

## Support

- 📖 Full documentation in `README.md`
-  Examples in `examples/` directory
-  Tests in `tests/` directory
- 🏃 Benchmarks in `benchmarks/` directory

## Performance Tips

1. **Use mock provider for testing** - No model overhead
2. **Use smaller models** - Mistral > Llama2 > Falcon in speed
3. **Enable quantization** - `mistral:7b-instruct-q4_0`
4. **Use GPU** - Set `AGENTFORGE_HF_DEVICE=cuda`
5. **Cache results** - Set `AGENTFORGE_ENABLE_CACHING=true`

## License

MIT License - See LICENSE file

---

