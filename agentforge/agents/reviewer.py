"""Code review and feedback agent."""

import json
from typing import Any, Dict
from agentforge.core.agent import Agent
from agentforge.core.task import Task


class ReviewerAgent(Agent):
    """Agent specialized in code review and quality assurance."""

    def __init__(self, llm_provider: Any):
        """Initialize reviewer agent."""
        super().__init__(
            name="reviewer",
            role="Code review and quality assurance specialist",
            llm_provider=llm_provider,
            system_prompt="""You are an expert code reviewer. Analyze code and:
1. Check correctness and logic
2. Find bugs and edge cases
3. Evaluate code quality and style
4. Assess performance and efficiency
5. Check for security issues
6. Provide specific, actionable feedback

Respond with JSON:
{
  "quality_score": 0-100,
  "issues": [
    {
      "severity": "critical|major|minor",
      "type": "bug|style|performance|security",
      "location": "line or function",
      "description": "what's wrong",
      "suggestion": "how to fix"
    }
  ],
  "overall_assessment": "summary",
  "recommendation": "approve|request_changes|reject"
}""",
        )

    def review_code(self, code: str, specification: str = "") -> Dict[str, Any]:
        """Review code for quality and correctness.

        Args:
            code: Code to review
            specification: Optional specification the code should follow

        Returns:
            Review feedback
        """
        import asyncio

        prompt = f"Review this code:\n```python\n{code}\n```"
        if specification:
            prompt += f"\n\nSpecification: {specification}"

        task = Task(
            description=prompt,
            constraints=["Provide constructive feedback", "Be specific"],
            max_iterations=5,
        )

        result = asyncio.run(self.think_and_act(task))

        try:
            review = json.loads(result.output)
        except:
            review = {
                "quality_score": 50,
                "issues": [],
                "overall_assessment": result.output,
                "recommendation": "request_changes",
            }

        return review

    def check_correctness(self, code: str, test_results: str) -> Dict[str, Any]:
        """Check if code passes tests.

        Args:
            code: Code to check
            test_results: Results from running tests

        Returns:
            Correctness assessment
        """
        import asyncio

        task = Task(
            description=f"Evaluate if this code is correct based on test results:\nCode:\n{code}\n\nTest Results:\n{test_results}",
            max_iterations=3,
        )

        result = asyncio.run(self.think_and_act(task))

        return {
            "assessment": result.output,
            "success": result.success,
        }
