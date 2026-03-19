"""Execution and task running agent."""

from typing import Any
from agentforge.core.agent import Agent, ToolDefinition
from agentforge.core.task import Task
from agentforge.tools.code_executor import execute_python_code
from agentforge.tools.file_manager import read_file, write_file, list_files


class ExecutorAgent(Agent):
    """Agent specialized in executing tasks and running code."""

    def __init__(self, llm_provider: Any):
        """Initialize executor agent."""
        tools = [
            ToolDefinition(
                name="execute_code",
                description="Execute Python code",
                func=execute_python_code,
                parameters={
                    "code": {"type": "string", "description": "Python code to run"}
                },
            ),
            ToolDefinition(
                name="read_file",
                description="Read a file",
                func=read_file,
                parameters={
                    "path": {"type": "string", "description": "File path"}
                },
            ),
            ToolDefinition(
                name="write_file",
                description="Write to a file",
                func=write_file,
                parameters={
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"},
                },
            ),
            ToolDefinition(
                name="list_files",
                description="List files in directory",
                func=list_files,
                parameters={
                    "directory": {
                        "type": "string",
                        "description": "Directory path",
                        "default": ".",
                    }
                },
            ),
        ]

        super().__init__(
            name="executor",
            role="Task execution and implementation specialist",
            llm_provider=llm_provider,
            tools=tools,
            system_prompt="""You are a task executor. Your job is to:
1. Execute code and commands
2. Manage files and data
3. Handle failures and errors gracefully
4. Report results clearly
5. Verify successful execution

Always check if actions succeeded and report issues.""",
        )

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command/task.

        Args:
            command: Command description or code

        Returns:
            Execution result
        """
        import asyncio

        task = Task(
            description=f"Execute this command: {command}",
            constraints=["Report success/failure", "Show output"],
            max_iterations=5,
        )

        result = asyncio.run(self.think_and_act(task))

        return {
            "success": result.success,
            "output": result.output,
            "trace": result.reasoning_trace,
        }
