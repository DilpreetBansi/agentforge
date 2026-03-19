"""Configuration management."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import json
from dataclasses import dataclass


@dataclass
class AgentForgeConfig:
    """AgentForge configuration."""

    # LLM settings
    llm_provider: str = "mock"  # mock, ollama, huggingface, openai
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    hf_model: str = "mistralai/Mistral-7B-Instruct-v0.1"
    hf_device: str = "cuda"
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

    # Agent settings
    max_iterations: int = 20
    max_tool_calls_per_step: int = 5
    code_execution_timeout: int = 30
    enable_reflection: bool = True

    # Orchestrator settings
    max_parallel_tasks: int = 4
    enable_caching: bool = True

    # Logging
    log_level: str = "INFO"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            k: v for k, v in self.__dict__.items() if v is not None
        }

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_env(cls) -> "AgentForgeConfig":
        """Load configuration from environment variables."""
        config = cls()

        # Read from env
        config.llm_provider = os.getenv("AGENTFORGE_LLM_PROVIDER", config.llm_provider)
        config.ollama_base_url = os.getenv(
            "AGENTFORGE_OLLAMA_BASE_URL", config.ollama_base_url
        )
        config.ollama_model = os.getenv("AGENTFORGE_OLLAMA_MODEL", config.ollama_model)
        config.hf_model = os.getenv("AGENTFORGE_HF_MODEL", config.hf_model)
        config.hf_device = os.getenv("AGENTFORGE_HF_DEVICE", config.hf_device)
        config.openai_api_key = os.getenv("OPENAI_API_KEY")
        config.openai_api_base = os.getenv("OPENAI_API_BASE")
        config.openai_model = os.getenv("OPENAI_MODEL", config.openai_model)
        config.max_iterations = int(
            os.getenv("AGENTFORGE_MAX_ITERATIONS", config.max_iterations)
        )
        config.enable_reflection = (
            os.getenv("AGENTFORGE_ENABLE_REFLECTION", "true").lower() == "true"
        )
        config.log_level = os.getenv("AGENTFORGE_LOG_LEVEL", config.log_level)

        return config

    @classmethod
    def from_file(cls, path: str) -> "AgentForgeConfig":
        """Load configuration from JSON file."""
        with open(path) as f:
            data = json.load(f)

        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        return config


def get_config() -> AgentForgeConfig:
    """Get current configuration (from env or defaults)."""
    return AgentForgeConfig.from_env()
