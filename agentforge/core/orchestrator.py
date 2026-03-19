"""Multi-agent task orchestrator."""

import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging
import time

from agentforge.core.agent import Agent
from agentforge.core.task import Task, SubTask, TaskResult, TaskStatus
from agentforge.core.memory import SharedMemory
from agentforge.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class OrchestrationConfig:
    """Configuration for orchestrator."""

    max_parallel_tasks: int = 4
    enable_reflection: bool = True
    enable_caching: bool = True
    default_timeout: int = 300  # seconds


class Orchestrator:
    """Orchestrates multiple agents to solve complex tasks."""

    def __init__(
        self,
        llm_provider: Any,
        config: Optional[OrchestrationConfig] = None,
    ):
        """Initialize orchestrator.

        Args:
            llm_provider: LLM provider instance
            config: Orchestration configuration
        """
        self.llm_provider = llm_provider
        self.config = config or OrchestrationConfig()
        self.shared_memory = SharedMemory()
        self.agents: Dict[str, Agent] = {}
        self._task_cache: Dict[str, TaskResult] = {}

    def register_agent(self, agent: Agent) -> None:
        """Register an agent."""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.role})")

    def _get_or_create_planner(self) -> Agent:
        """Get or create planner agent."""
        if "planner" not in self.agents:
            planner = Agent(
                name="planner",
                role="Task planning and decomposition specialist",
                llm_provider=self.llm_provider,
                system_prompt="""You are a task planning specialist. Your job is to:
1. Analyze complex tasks and break them into smaller subtasks
2. Identify dependencies between subtasks
3. Suggest the best agent for each subtask
4. Create an execution plan

Always structure your response as JSON with:
{
  "subtasks": [
    {"description": "...", "agent": "...", "dependencies": []}
  ],
  "reasoning": "..."
}""",
            )
            self.register_agent(planner)
        return self.agents["planner"]

    def _get_or_create_verifier(self) -> Agent:
        """Get or create verifier agent."""
        if "verifier" not in self.agents:
            verifier = Agent(
                name="verifier",
                role="Result verification specialist",
                llm_provider=self.llm_provider,
                system_prompt="""You are a verification specialist. Your job is to:
1. Check if the solution meets all requirements
2. Verify the solution is correct
3. Identify any issues or gaps
4. Provide a final verdict

Respond with:
{
  "verified": true/false,
  "issues": [...],
  "feedback": "..."
}""",
            )
            self.register_agent(verifier)
        return self.agents["verifier"]

    async def execute_task(
        self,
        task_description: str,
        context: str = "",
        constraints: Optional[List[str]] = None,
        max_iterations: int = 20,
    ) -> TaskResult:
        """Execute a task using multi-agent orchestration.

        Args:
            task_description: Description of task to solve
            context: Additional context
            constraints: List of constraints
            max_iterations: Maximum iterations per agent

        Returns:
            TaskResult with final output and reasoning trace
        """
        task = Task(
            description=task_description,
            context=context,
            constraints=constraints or [],
            max_iterations=max_iterations,
            enable_reflection=self.config.enable_reflection,
        )

        logger.info(f"Executing task: {task.description[:50]}...")
        start_time = time.time()

        # Check cache
        cache_key = f"{task_description}:{context}"
        if self.config.enable_caching and cache_key in self._task_cache:
            logger.info("Using cached result")
            return self._task_cache[cache_key]

        # Step 1: Decompose task
        planner = self._get_or_create_planner()
        planning_task = Task(
            description=f"Decompose this task into subtasks:\n{task_description}",
            context=context,
            max_iterations=5,
        )

        plan_result = await planner.think_and_act(
            planning_task, self.shared_memory
        )

        # Step 2: Execute subtasks
        if len(self.agents) > 1:
            # Multi-agent execution
            main_result = await self._execute_with_agents(task, plan_result)
        else:
            # Single agent fallback
            main_agent = Agent(
                name="executor",
                role="General task executor",
                llm_provider=self.llm_provider,
            )
            main_result = await main_agent.think_and_act(task, self.shared_memory)

        # Step 3: Verify result
        if self.config.enable_reflection:
            verifier = self._get_or_create_verifier()
            verification_task = Task(
                description=f"Verify this solution:\n{main_result.output}",
                context=f"Original task: {task_description}",
                max_iterations=5,
            )
            verification_result = await verifier.think_and_act(
                verification_task, self.shared_memory
            )
            main_result.add_reasoning_step(
                f"Verification: {verification_result.output}"
            )

        # Add metrics
        elapsed = time.time() - start_time
        main_result.add_metric("elapsed_time_seconds", elapsed)
        main_result.add_metric("num_agents", len(self.agents))

        # Cache result
        if self.config.enable_caching:
            self._task_cache[cache_key] = main_result

        logger.info(
            f"Task completed in {elapsed:.2f}s with result: {main_result.success}"
        )

        return main_result

    async def _execute_with_agents(
        self, task: Task, plan_result: TaskResult
    ) -> TaskResult:
        """Execute task using specialized agents."""
        main_result = TaskResult(task_id=task.task_id, success=False, output="")

        try:
            # Try to parse plan
            import json

            plan_data = json.loads(plan_result.output)
            subtasks = plan_data.get("subtasks", [])
        except:
            # Fallback if plan parsing fails
            subtasks = [
                {
                    "description": task.description,
                    "agent": "executor",
                    "dependencies": [],
                }
            ]

        # Execute subtasks in dependency order
        results = {}
        for subtask_info in subtasks:
            description = subtask_info.get("description", task.description)
            agent_name = subtask_info.get("agent", "executor")

            # Get or create agent
            if agent_name not in self.agents:
                agent = Agent(
                    name=agent_name,
                    role=agent_name,
                    llm_provider=self.llm_provider,
                )
                self.register_agent(agent)
            else:
                agent = self.agents[agent_name]

            # Execute subtask
            subtask = Task(
                description=description,
                context=task.context,
                max_iterations=task.max_iterations,
            )

            result = await agent.think_and_act(subtask, self.shared_memory)
            results[agent_name] = result

            if result.success:
                main_result.output += f"\n{agent_name}: {result.output}"
                main_result.subtask_results[agent_name] = result

        main_result.success = any(r.success for r in results.values())
        return main_result

    async def execute_tasks_parallel(
        self, task_descriptions: List[str]
    ) -> List[TaskResult]:
        """Execute multiple tasks in parallel.

        Args:
            task_descriptions: List of task descriptions

        Returns:
            List of TaskResults
        """
        tasks = [
            Task(description=desc, max_iterations=20) for desc in task_descriptions
        ]

        # Execute with concurrency limit
        semaphore = asyncio.Semaphore(self.config.max_parallel_tasks)

        async def execute_with_limit(task: Task) -> TaskResult:
            async with semaphore:
                return await self.execute_task(task.description)

        results = await asyncio.gather(
            *[execute_with_limit(task) for task in tasks],
            return_exceptions=False,
        )

        return results

    def clear_cache(self) -> None:
        """Clear task result cache."""
        self._task_cache.clear()
        logger.info("Task cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "num_agents": len(self.agents),
            "cache_size": len(self._task_cache),
            "shared_memory_entries": self.shared_memory.size(),
            "agents": list(self.agents.keys()),
        }
