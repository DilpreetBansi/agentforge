"""HuggingFace transformers local model provider."""

from typing import Any, Dict, List, Optional
import os
import logging

from agentforge.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class HuggingFaceProvider(BaseLLMProvider):
    """LLM provider using HuggingFace transformers for local model serving."""

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.1",
        device: str = "cuda",
        max_memory: Optional[Dict[int, str]] = None,
        **kwargs,
    ):
        """Initialize HuggingFace provider.

        Args:
            model_name: HuggingFace model name
            device: Device to use ('cuda' or 'cpu')
            max_memory: Memory limits per GPU
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.model_name = model_name
        self.device = device
        self.max_memory = max_memory
        self.model = None
        self.tokenizer = None

        # Allow override from environment
        self.model_name = os.getenv("AGENTFORGE_HF_MODEL", self.model_name)
        self.device = os.getenv("AGENTFORGE_HF_DEVICE", self.device)

    def _load_model(self):
        """Load model and tokenizer on first use."""
        if self.model is not None:
            return

        logger.info(f"Loading HuggingFace model: {self.model_name}")

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError:
            raise ImportError(
                "transformers and torch required. Install with: pip install transformers torch"
            )

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # Set up device memory management
            device_map = "auto" if self.device == "cuda" else None

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=device_map,
                max_memory=self.max_memory,
            )

            logger.info(f"Model loaded successfully on {self.device}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate response using HuggingFace model.

        Args:
            messages: Conversation messages
            tools: Available tools (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Returns:
            Response dictionary
        """
        self._load_model()

        # Format messages into prompt
        prompt = self._format_prompt(messages, tools)

        logger.debug(f"Generating with max_tokens={max_tokens}, temp={temperature}")

        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            # Generate
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                do_sample=True,
            )

            # Decode output
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove prompt from output
            response = response_text[len(prompt) :].strip()

            return {
                "response": response,
                "thinking": "",
                "done": True,
                "tool_calls": [],
            }

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                "response": f"Error: {str(e)}",
                "done": True,
            }

    def _format_prompt(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Format messages into a prompt."""
        prompt_parts = []

        # Add system prompt if present
        for msg in messages:
            if msg.get("role") == "system":
                prompt_parts.append(f"{msg.get('content', '')}\n\n")

        # Add tools context
        if tools:
            prompt_parts.append("Available tools:\n")
            for tool in tools:
                prompt_parts.append(f"- {tool.get('name')}: {tool.get('description')}\n")
            prompt_parts.append("\n")

        # Add conversation
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                continue
            elif role == "user":
                prompt_parts.append(f"User: {msg.get('content', '')}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {msg.get('content', '')}\n")

        prompt_parts.append("Assistant: ")

        return "".join(prompt_parts)
