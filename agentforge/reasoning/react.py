"""ReAct (Reasoning + Acting) implementation."""

from typing import Any, Dict, List, Optional
import json
import re


class ReActReasoner:
    """Implements ReAct reasoning: Thought -> Action -> Observation loop."""

    def __init__(self, llm_provider: Any):
        """Initialize ReAct reasoner.

        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider

    async def reason_and_act(
        self,
        problem: str,
        tools: Optional[Dict[str, Any]] = None,
        max_steps: int = 10,
    ) -> Dict[str, Any]:
        """Perform ReAct reasoning and acting.

        Args:
            problem: Problem to solve
            tools: Available tools
            max_steps: Maximum reasoning steps

        Returns:
            Solution with full reasoning trace
        """
        tools = tools or {}
        reasoning_trace = []
        step = 0

        # Initial prompt
        prompt = f"""You are a helpful assistant that can reason and act.

Problem: {problem}

Available tools: {list(tools.keys())}

Respond in this format:
Thought: [your reasoning]
Action: [tool_name with parameters]
Observation: [result]

Repeat until done. When ready to answer, respond with:
Final Answer: [your answer]"""

        messages = [{"role": "user", "content": prompt}]

        while step < max_steps:
            step += 1

            # Get LLM response
            response = await self.llm_provider.generate(
                messages=messages,
                temperature=0.7,
            )

            output = response.get("response", "")
            reasoning_trace.append(output)

            # Check if done
            if "Final Answer:" in output:
                final_answer = output.split("Final Answer:")[-1].strip()
                return {
                    "success": True,
                    "answer": final_answer,
                    "reasoning_trace": reasoning_trace,
                    "num_steps": step,
                }

            # Parse thought and action
            thought = self._extract_thought(output)
            action = self._extract_action(output)

            if not action:
                # No action found, might be done or confused
                return {
                    "success": False,
                    "answer": output,
                    "reasoning_trace": reasoning_trace,
                    "num_steps": step,
                }

            # Execute action
            tool_name, tool_input = self._parse_action(action)
            if tool_name in tools:
                try:
                    observation = tools[tool_name](**tool_input)
                except Exception as e:
                    observation = f"Error: {str(e)}"
            else:
                observation = f"Tool '{tool_name}' not found"

            # Add to messages
            messages.append({"role": "assistant", "content": output})
            messages.append(
                {
                    "role": "user",
                    "content": f"Observation: {observation}\n\nContinue reasoning...",
                }
            )

        return {
            "success": False,
            "answer": "Max steps reached",
            "reasoning_trace": reasoning_trace,
            "num_steps": step,
        }

    @staticmethod
    def _extract_thought(output: str) -> Optional[str]:
        """Extract thought from output."""
        match = re.search(r"Thought:\s*(.+?)(?=Action:|$)", output, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def _extract_action(output: str) -> Optional[str]:
        """Extract action from output."""
        match = re.search(r"Action:\s*(.+?)(?=Observation:|$)", output, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def _parse_action(action: str) -> tuple[str, Dict[str, Any]]:
        """Parse action into tool name and parameters."""
        # Try JSON format: {"tool": "name", "input": {...}}
        try:
            action_json = json.loads(action)
            return action_json.get("tool", ""), action_json.get("input", {})
        except:
            pass

        # Try simple format: tool_name(param1=value1, param2=value2)
        match = re.match(r"(\w+)\((.*)\)", action)
        if match:
            tool_name = match.group(1)
            params_str = match.group(2)
            # Simple param parsing
            params = {}
            for param in params_str.split(","):
                if "=" in param:
                    k, v = param.split("=", 1)
                    params[k.strip()] = v.strip().strip("\"'")
            return tool_name, params

        return "", {}


def format_react_prompt(problem: str, tools: Optional[List[str]] = None) -> str:
    """Format a problem for ReAct reasoning.

    Args:
        problem: Problem statement
        tools: Available tools

    Returns:
        Formatted prompt for ReAct
    """
    tools_text = ""
    if tools:
        tools_text = f"\nAvailable tools: {', '.join(tools)}"

    return f"""Solve this problem using reasoning and actions.

{problem}{tools_text}

Format your response as:
Thought: [reasoning about what to do]
Action: [action to take]
Observation: [result of action]

Repeat until you have the answer, then provide:
Final Answer: [your solution]"""
