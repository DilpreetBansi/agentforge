"""Code generation and writing agent."""

from agentforge.core.agent import Agent, ToolDefinition
from agentforge.core.task import Task
from agentforge.tools.code_executor import execute_python_code
from typing import Any, Dict


class CoderAgent(Agent):
    """Agent specialized in writing and testing code."""

    def __init__(self, llm_provider: Any):
        """Initialize coder agent."""
        tools = [
            ToolDefinition(
                name="execute_code",
                description="Execute Python code and get results",
                func=execute_python_code,
                parameters={
                    "code": {
                        "type": "string",
                        "description": "Python code to execute",
                    }
                },
            ),
        ]

        super().__init__(
            name="coder",
            role="Code generation and implementation specialist",
            llm_provider=llm_provider,
            tools=tools,
            system_prompt="""You are an expert Python programmer. Your job is to:
1. Write clean, correct, well-documented code
2. Test code with provided test cases
3. Debug and fix issues iteratively
4. Provide the final working solution

When writing code:
- Always include docstrings
- Use type hints
- Handle edge cases
- Test thoroughly before declaring success

When you have a working solution, respond with:
```python
[final code here]
```

Then say "SOLUTION_COMPLETE" when done.""",
        )

    def generate_code(self, specification: str) -> str:
        """Generate code based on specification.

        Args:
            specification: Description of what code to write

        Returns:
            Generated code as string
        """
        import asyncio

        task = Task(
            description=f"Write code based on this specification:\n{specification}",
            constraints=["Code must be testable", "Must include documentation"],
            max_iterations=10,
        )

        result = asyncio.run(self.think_and_act(task))
        return result.output


class TestGeneratorAgent(Agent):
    """Agent for generating test cases."""

    def __init__(self, llm_provider: Any):
        """Initialize test generator agent."""
        super().__init__(
            name="test_generator",
            role="Test case generation specialist",
            llm_provider=llm_provider,
            system_prompt="""You are a QA specialist. Generate comprehensive test cases:
1. Normal cases
2. Edge cases
3. Error cases
4. Boundary conditions

Format as pytest test functions.""",
        )

    def generate_tests(self, code: str, description: str) -> str:
        """Generate test cases for code.

        Args:
            code: Code to test
            description: Description of what code does

        Returns:
            Test code as string
        """
        import asyncio

        task = Task(
            description=f"Generate tests for:\n{code}\n\nDescription: {description}",
            max_iterations=5,
        )

        result = asyncio.run(self.think_and_act(task))
        return result.output
