"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM."""

    response: str
    thinking: str = ""
    done: bool = False
    tool_calls: List[Dict[str, Any]] = None
    tokens_used: int = 0

    def __post_init__(self):
        """Initialize."""
        if self.tool_calls is None:
            self.tool_calls = []


class BaseLLMProvider(ABC):
    """Base class for all LLM providers."""

    def __init__(self, **kwargs):
        """Initialize LLM provider."""
        self.kwargs = kwargs

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate response from messages.

        Args:
            messages: Conversation messages
            tools: Available tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments

        Returns:
            Response dictionary with 'response' key
        """
        pass

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        **kwargs,
    ):
        """Stream response tokens (optional).

        Args:
            messages: Conversation messages
            tools: Available tools
            temperature: Sampling temperature
            **kwargs: Additional arguments

        Yields:
            Response tokens
        """
        # Default: just return full response
        response = await self.generate(messages, tools, temperature, **kwargs)
        yield response
