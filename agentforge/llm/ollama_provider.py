"""Ollama local model provider."""

import asyncio
import aiohttp
from typing import Any, Dict, List, Optional
import json
import os

from agentforge.llm.base import BaseLLMProvider
from agentforge.utils.logging import get_logger

logger = get_logger(__name__)


class OllamaLLMProvider(BaseLLMProvider):
    """LLM provider using Ollama for local model serving."""

    def __init__(
        self,
        model: str = "mistral",
        base_url: str = "http://localhost:11434",
        timeout: int = 300,
        **kwargs,
    ):
        """Initialize Ollama provider.

        Args:
            model: Model name (e.g., 'mistral', 'llama2', 'codellama')
            base_url: Ollama server URL
            timeout: Request timeout in seconds
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Allow override from environment
        self.base_url = os.getenv("AGENTFORGE_OLLAMA_BASE_URL", self.base_url)
        self.model = os.getenv("AGENTFORGE_OLLAMA_MODEL", self.model)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate response using Ollama.

        Args:
            messages: Conversation messages
            tools: Available tools (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Returns:
            Response dictionary
        """
        # Format messages for Ollama
        prompt = self._format_prompt(messages, tools)

        logger.debug(f"Calling Ollama with model: {self.model}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": temperature,
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama error: {error_text}")
                        return {
                            "response": f"Error: {response.status} - {error_text[:100]}",
                            "done": True,
                        }

                    data = await response.json()
                    text = data.get("response", "")

                    return {
                        "response": text.strip(),
                        "thinking": "",
                        "done": True,
                        "tool_calls": [],
                    }

        except asyncio.TimeoutError:
            logger.error("Ollama request timed out")
            return {
                "response": f"Error: Request timed out after {self.timeout}s. Is Ollama running?",
                "done": True,
            }
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            return {
                "response": f"Error: Cannot connect to Ollama at {self.base_url}. Is it running?",
                "done": True,
            }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {
                "response": f"Error: {str(e)}",
                "done": True,
            }

    def _format_prompt(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Format messages into a prompt for Ollama."""
        prompt_parts = []

        # Add system prompt if present
        for msg in messages:
            if msg.get("role") == "system":
                prompt_parts.append(f"System: {msg.get('content', '')}\n")

        # Add tools context if provided
        if tools:
            prompt_parts.append("\nAvailable tools:\n")
            for tool in tools:
                prompt_parts.append(f"- {tool.get('name')}: {tool.get('description')}\n")
            prompt_parts.append("\n")

        # Add conversation history
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                continue  # Already added
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
            else:
                prompt_parts.append(f"{role}: {content}\n")

        prompt_parts.append("Assistant: ")

        return "".join(prompt_parts)

    async def list_models(self) -> List[str]:
        """List available models on the Ollama server."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        return [m.get("name", "") for m in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")

        return []
