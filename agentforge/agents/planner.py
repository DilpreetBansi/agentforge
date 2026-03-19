"""Task planning and decomposition agent."""

import json
from typing import Any, List, Dict, Optional
from agentforge.core.agent import Agent
from agentforge.core.task import Task, SubTask


class PlannerAgent(Agent):
    """Agent specialized in task decomposition and planning."""

    def __init__(self, llm_provider: Any):
        """Initialize planner agent."""
        super().__init__(
            name="planner",
            role="Task decomposition and planning specialist",
            llm_provider=llm_provider,
            system_prompt="""You are an expert task planner. Analyze complex tasks and:
1. Break them into logical subtasks
2. Identify dependencies between subtasks
3. Assign tasks to appropriate agents (coder, researcher, reviewer, executor)
4. Create an execution plan in DAG order

Respond with JSON:
{
  "subtasks": [
    {
      "id": "task_1",
      "description": "...",
      "agent": "coder|researcher|reviewer|executor",
      "dependencies": [],
      "difficulty": "easy|medium|hard",
      "estimated_iterations": 5
    }
  ],
  "critical_path": ["task_1", "task_2"],
  "reasoning": "explanation of plan"
}""",
        )

    def decompose_task(self, task_description: str) -> Dict[str, Any]:
        """Decompose a task into subtasks.

        Args:
            task_description: Task to decompose

        Returns:
            Dictionary with subtasks and dependencies
        """
        import asyncio

        task = Task(
            description=f"Decompose this task:\n{task_description}",
            max_iterations=5,
        )

        result = asyncio.run(self.think_and_act(task))

        try:
            plan = json.loads(result.output)
        except:
            plan = {
                "subtasks": [
                    {
                        "id": "task_1",
                        "description": task_description,
                        "agent": "executor",
                        "dependencies": [],
                        "estimated_iterations": 10,
                    }
                ],
                "critical_path": ["task_1"],
                "reasoning": "Could not parse plan",
            }

        return plan

    def create_execution_plan(
        self, subtasks: List[Dict[str, Any]]
    ) -> List[SubTask]:
        """Create execution plan from subtasks.

        Args:
            subtasks: List of subtask descriptions

        Returns:
            List of SubTask objects with dependencies
        """
        execution_plan = []

        for subtask_info in subtasks:
            subtask = SubTask(
                parent_task_id="main",
                description=subtask_info.get("description", ""),
                assigned_agent=subtask_info.get("agent", "executor"),
                dependencies=subtask_info.get("dependencies", []),
            )
            execution_plan.append(subtask)

        return execution_plan

    def estimate_complexity(self, task_description: str) -> Dict[str, Any]:
        """Estimate task complexity and effort.

        Args:
            task_description: Task to estimate

        Returns:
            Complexity metrics
        """
        import asyncio

        task = Task(
            description=f"Estimate the complexity of this task:\n{task_description}\n\nProvide JSON with: difficulty (easy|medium|hard), estimated_iterations (1-20), required_tools (list)",
            max_iterations=3,
        )

        result = asyncio.run(self.think_and_act(task))

        try:
            complexity = json.loads(result.output)
        except:
            complexity = {
                "difficulty": "medium",
                "estimated_iterations": 10,
                "required_tools": ["code_executor"],
            }

        return complexity
