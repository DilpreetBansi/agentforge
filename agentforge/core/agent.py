"""Base Agent class with reasoning loop."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import json
import logging

from agentforge.core.message import Message, AgentMessage, ToolCall, ToolResult
from agentforge.core.task import Task, TaskResult
from agentforge.core.memory import SharedMemory
from agentforge.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ToolDefinition:
    """Definition of a tool available to agents."""

    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(
        self,
        name: str,
        role: str,
        llm_provider: Any,
        tools: Optional[List[ToolDefinition]] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize agent.

        Args:
            name: Agent's name
            role: Agent's role/description
            llm_provider: LLM provider instance
            tools: List of tools available to agent
            system_prompt: System prompt for agent
        """
        self.name = name
        self.role = role
        self.llm_provider = llm_provider
        self.tools = tools or []
        self.system_prompt = system_prompt or f"You are {name}, a {role}. Help solve tasks effectively."
        self.memory = SharedMemory()
        self.max_iterations = 20
        self.iteration_count = 0

    def add_tool(self, tool: ToolDefinition) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)

    def get_tools_description(self) -> str:
        """Get formatted description of available tools."""
        if not self.tools:
            return "No tools available."

        tools_text = "Available tools:\n"
        for tool in self.tools:
            tools_text += f"- {tool.name}: {tool.description}\n"
        return tools_text

    async def think_and_act(
        self, task: Task, shared_memory: Optional[SharedMemory] = None
    ) -> TaskResult:
        """Main reasoning loop: observe -> reason -> act -> observe.

        Args:
            task: Task to solve
            shared_memory: Optional shared memory from orchestrator

        Returns:
            TaskResult with output and metrics
        """
        self.iteration_count = 0
        shared_memory = shared_memory or self.memory
        result = TaskResult(task_id=task.task_id, success=False, output="")

        logger.info(f"[{self.name}] Starting task: {task.description}")

        # Initial prompt
        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": f"Task: {task.description}\n\nContext: {task.context}\n\nConstraints: {', '.join(task.constraints)}",
            },
        ]

        # ReAct loop
        while self.iteration_count < task.max_iterations:
            self.iteration_count += 1
            logger.debug(f"[{self.name}] Iteration {self.iteration_count}")

            # Get LLM response with tools
            try:
                response = await self._call_llm(messages)
            except Exception as e:
                result.error = str(e)
                result.add_reasoning_step(f"LLM error: {str(e)}")
                logger.error(f"[{self.name}] LLM error: {e}")
                break

            result.add_reasoning_step(response.get("thinking", ""))

            # Check if done
            if response.get("done", False):
                result.success = True
                result.output = response.get("response", "")
                result.add_reasoning_step(f"Task completed: {result.output}")
                logger.info(f"[{self.name}] Task completed successfully")
                break

            # Parse tool calls
            tool_calls = response.get("tool_calls", [])
            if not tool_calls:
                # No tool calls but not done - output response
                result.success = True
                result.output = response.get("response", "")
                result.add_reasoning_step(f"Final response: {result.output}")
                break

            # Execute tools
            for tool_call in tool_calls:
                tool_name = tool_call.get("name", "")
                tool_input = tool_call.get("input", {})

                tool_result = await self._execute_tool(tool_name, tool_input)
                result.add_reasoning_step(
                    f"Tool {tool_name} result: {tool_result['result'][:100]}"
                )

                # Add to messages for next iteration
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(tool_call),
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Tool result:\n{tool_result['result']}",
                    }
                )

        result.add_metric("iterations", self.iteration_count)
        logger.info(
            f"[{self.name}] Task finished in {self.iteration_count} iterations"
        )

        return result

    async def _call_llm(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call LLM with messages."""
        tools_json = self._serialize_tools()
        response = await self.llm_provider.generate(
            messages=messages,
            tools=tools_json,
            temperature=0.7,
        )
        return response

    def _serialize_tools(self) -> List[Dict[str, Any]]:
        """Serialize tools for LLM."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self.tools
        ]

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    if asyncio.iscoroutinefunction(tool.func):
                        result = await tool.func(**tool_input)
                    else:
                        result = tool.func(**tool_input)
                    return {"success": True, "result": str(result)}
                except Exception as e:
                    return {"success": False, "result": f"Error: {str(e)}"}

        return {"success": False, "result": f"Tool '{tool_name}' not found"}

    @abstractmethod
    def system_instructions(self) -> str:
        """Get system instructions for this agent."""
        pass


class Agent(BaseAgent):
    """General-purpose agent."""

    def system_instructions(self) -> str:
        """Get system instructions."""
        return self.system_prompt


class ReflectiveAgent(BaseAgent):
    """Agent with self-reflection capabilities."""

    def __init__(self, *args, **kwargs):
        """Initialize reflective agent."""
        super().__init__(*args, **kwargs)
        self.reflection_enabled = True

    async def think_and_act(
        self, task: Task, shared_memory: Optional[SharedMemory] = None
    ) -> TaskResult:
        """Run with optional reflection on failure."""
        result = await super().think_and_act(task, shared_memory)

        # Reflect on failure if enabled
        if not result.success and self.reflection_enabled and self.iteration_count > 0:
            logger.info(f"[{self.name}] Reflecting on failure...")
            reflection_result = await self._reflect_and_retry(task, result)
            if reflection_result.success:
                return reflection_result

        return result

    async def _reflect_and_retry(
        self, task: Task, failed_result: TaskResult
    ) -> TaskResult:
        """Reflect on failure and retry."""
        reflection_prompt = f"""
You failed to solve this task:
{task.description}

Error: {failed_result.error}
Reasoning trace:
{chr(10).join(failed_result.reasoning_trace[-5:])}

Analyze what went wrong and try a different approach.
"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": reflection_prompt},
        ]

        logger.debug(f"[{self.name}] Running reflection...")
        response = await self._call_llm(messages)

        # Create new task with insights
        new_task = Task(
            description=task.description,
            context=f"{task.context}\n\nPrevious attempt failed. {response.get('thinking', '')}",
            constraints=task.constraints,
            max_iterations=min(10, task.max_iterations // 2),
        )

        return await super().think_and_act(new_task)

    def system_instructions(self) -> str:
        """Get system instructions."""
        return self.system_prompt
