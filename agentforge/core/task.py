"""Task and result data structures."""

from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from enum import Enum
import json


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Represents a user task to be solved by agents."""

    description: str
    context: str = ""
    constraints: List[str] = field(default_factory=list)
    task_id: str = field(default_factory=lambda: f"task_{id(object())}")
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0  # Higher = more important
    max_iterations: int = 20
    enable_reflection: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "context": self.context,
            "constraints": self.constraints,
            "status": self.status.value,
            "priority": self.priority,
            "max_iterations": self.max_iterations,
            "enable_reflection": self.enable_reflection,
            "metadata": self.metadata,
        }


@dataclass
class SubTask:
    """Represents a subtask broken down from main task."""

    parent_task_id: str
    description: str
    assigned_agent: Optional[str] = None  # Agent name
    dependencies: List[str] = field(default_factory=list)  # IDs of subtasks this depends on
    subtask_id: str = field(default_factory=lambda: f"subtask_{id(object())}")
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subtask_id": self.subtask_id,
            "parent_task_id": self.parent_task_id,
            "description": self.description,
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    success: bool
    output: str
    reasoning_trace: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    subtask_results: Dict[str, "TaskResult"] = field(default_factory=dict)
    error: Optional[str] = None
    intermediate_steps: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "reasoning_trace": self.reasoning_trace,
            "metrics": self.metrics,
            "error": self.error,
            "intermediate_steps": self.intermediate_steps,
            "subtask_results": {
                k: v.to_dict() for k, v in self.subtask_results.items()
            },
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def add_reasoning_step(self, step: str) -> None:
        """Add a reasoning step to the trace."""
        self.reasoning_trace.append(step)

    def add_metric(self, name: str, value: Any) -> None:
        """Add a metric."""
        self.metrics[name] = value

    def add_subtask_result(self, subtask_id: str, result: "TaskResult") -> None:
        """Add result from a subtask."""
        self.subtask_results[subtask_id] = result


@dataclass
class ExecutionMetrics:
    """Metrics collected during task execution."""

    total_iterations: int = 0
    total_tool_calls: int = 0
    total_tokens_used: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    errors_encountered: List[str] = field(default_factory=list)
    reasoning_depth: int = 0  # How deep the reasoning went

    def elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_iterations": self.total_iterations,
            "total_tool_calls": self.total_tool_calls,
            "total_tokens_used": self.total_tokens_used,
            "elapsed_time_seconds": self.elapsed_time(),
            "reasoning_depth": self.reasoning_depth,
            "errors_encountered": self.errors_encountered,
        }
