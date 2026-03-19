"""Message types for inter-agent communication."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Dict, List
import json


@dataclass
class Message:
    """Base message class for agent communication."""

    sender: str  # Agent name or "user" or "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "generic"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert message to JSON."""
        return json.dumps(self.to_dict())


@dataclass
class UserMessage(Message):
    """Message from user to agent system."""

    message_type: str = "user"


@dataclass
class SystemMessage(Message):
    """System-level message with directives."""

    message_type: str = "system"


@dataclass
class AgentMessage(Message):
    """Message from one agent to another or back to user."""

    message_type: str = "agent"
    reasoning: Optional[str] = None  # Agent's reasoning process


@dataclass
class ToolCall(Message):
    """Agent request to execute a tool."""

    message_type: str = "tool_call"
    tool_name: str = ""
    tool_input: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["tool_name"] = self.tool_name
        d["tool_input"] = self.tool_input
        return d


@dataclass
class ToolResult(Message):
    """Result from tool execution."""

    message_type: str = "tool_result"
    tool_name: str = ""
    success: bool = True
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["tool_name"] = self.tool_name
        d["success"] = self.success
        d["result"] = str(self.result) if self.result else None
        d["error"] = self.error
        return d


@dataclass
class ConversationHistory:
    """Maintains conversation history for context."""

    messages: List[Message] = field(default_factory=list)

    def add_message(self, message: Message) -> None:
        """Add message to history."""
        self.messages.append(message)

    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Get recent messages."""
        if limit is None:
            return self.messages
        return self.messages[-limit:]

    def get_by_sender(self, sender: str) -> List[Message]:
        """Get messages from specific sender."""
        return [m for m in self.messages if m.sender == sender]

    def get_by_type(self, message_type: str) -> List[Message]:
        """Get messages of specific type."""
        return [m for m in self.messages if m.message_type == message_type]

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []

    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert history to list of dicts."""
        return [m.to_dict() for m in self.messages]
