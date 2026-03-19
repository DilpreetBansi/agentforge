"""Dynamic tool registration system."""

from typing import Any, Callable, Dict, Optional
from functools import wraps
import json
import inspect


class ToolRegistry:
    """Registry for dynamically discovering and registering tools."""

    _tools: Dict[str, "ToolDefinition"] = {}

    @dataclass
    class ToolDefinition:
        """Definition of a tool."""

        name: str
        description: str
        func: Callable
        parameters: Dict[str, Any]

    @classmethod
    def register(
        cls,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Decorator to register a tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON Schema for parameters
        """

        def decorator(func: Callable) -> Callable:
            sig = inspect.signature(func)
            params = parameters or {}

            # Auto-generate parameter schema from function signature
            if not params:
                for param_name, param in sig.parameters.items():
                    if param_name != "self":
                        param_type = "string"  # Default to string
                        if param.annotation != inspect.Parameter.empty:
                            if param.annotation == int:
                                param_type = "integer"
                            elif param.annotation == float:
                                param_type = "number"
                            elif param.annotation == bool:
                                param_type = "boolean"

                        params[param_name] = {
                            "type": param_type,
                            "description": f"Parameter: {param_name}",
                        }

            tool_def = cls.ToolDefinition(
                name=name, description=description, func=func, parameters=params
            )

            cls._tools[name] = tool_def

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Optional["ToolDefinition"]:
        """Get tool by name."""
        return cls._tools.get(name)

    @classmethod
    def get_all_tools(cls) -> Dict[str, "ToolDefinition"]:
        """Get all registered tools."""
        return cls._tools.copy()

    @classmethod
    def get_tools_json(cls) -> list:
        """Get all tools as JSON schema."""
        tools = []
        for tool in cls._tools.values():
            tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            )
        return tools

    @classmethod
    def execute_tool(cls, name: str, **kwargs) -> Any:
        """Execute a registered tool."""
        tool = cls.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool.func(**kwargs)


# Import dataclasses
from dataclasses import dataclass
