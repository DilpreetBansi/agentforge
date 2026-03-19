"""OpenAI API provider - supports official API and compatible endpoints."""

from typing import Any, Dict, List, Optional
import os
import asyncio
import aiohttp
import json

from agentforge.llm.base import BaseLLMProvider
from agentforge.utils.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """LLM provider using OpenAI API or compatible endpoints."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        api_base: Optional[str] = None,
        **kwargs,
    ):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (from env if not provided)
            model: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4')
            api_base: Custom API base URL for compatible endpoints
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.api_base = (
            api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable."
            )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate response using OpenAI API.

        Args:
            messages: Conversation messages
            tools: Available tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional arguments

        Returns:
            Response dictionary
        """
        logger.debug(f"Calling OpenAI model: {self.model}")

        # Prepare request
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add tools if provided
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.get("name"),
                        "description": tool.get("description"),
                        "parameters": tool.get("parameters", {}),
                    },
                }
                for tool in tools
            ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {error_text}")
                        return {
                            "response": f"Error: {error_text[:100]}",
                            "done": True,
                        }

                    data = await response.json()
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})

                    # Extract response or tool calls
                    if "tool_calls" in message:
                        tool_calls = [
                            {
                                "name": tc.get("function", {}).get("name"),
                                "input": json.loads(
                                    tc.get("function", {}).get("arguments", "{}")
                                ),
                            }
                            for tc in message.get("tool_calls", [])
                        ]
                        response_text = message.get("content", "")
                    else:
                        tool_calls = []
                        response_text = message.get("content", "")

                    return {
                        "response": response_text.strip(),
                        "thinking": "",
                        "done": True,
                        "tool_calls": tool_calls,
                    }

        except asyncio.TimeoutError:
            logger.error("OpenAI request timed out")
            return {
                "response": "Error: Request timed out",
                "done": True,
            }
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {
                "response": f"Error: {str(e)}",
                "done": True,
            }
