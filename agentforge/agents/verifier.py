"""Result verification and validation agent."""

import json
from typing import Any, Dict
from agentforge.core.agent import Agent
from agentforge.core.task import Task


class VerifierAgent(Agent):
    """Agent specialized in verifying results and validating solutions."""

    def __init__(self, llm_provider: Any):
        """Initialize verifier agent."""
        super().__init__(
            name="verifier",
            role="Result verification and validation specialist",
            llm_provider=llm_provider,
            system_prompt="""You are a verification specialist. Your job is to:
1. Check if results meet requirements
2. Validate correctness
3. Identify gaps or missing elements
4. Provide final verdict

Respond with JSON:
{
  "verified": true/false,
  "confidence": 0-100,
  "issues": ["list of issues if any"],
  "missing_elements": ["anything not addressed"],
  "feedback": "detailed feedback",
  "recommendation": "accept|request_changes|reject"
}""",
        )

    def verify_result(
        self, result: str, requirements: str = "", success_criteria: str = ""
    ) -> Dict[str, Any]:
        """Verify if a result meets requirements.

        Args:
            result: Result/output to verify
            requirements: Original requirements
            success_criteria: What defines success

        Returns:
            Verification report
        """
        import asyncio

        prompt = f"Verify this result:\n{result}"
        if requirements:
            prompt += f"\n\nRequirements: {requirements}"
        if success_criteria:
            prompt += f"\n\nSuccess criteria: {success_criteria}"

        task = Task(
            description=prompt,
            constraints=["Be thorough", "Provide specific feedback"],
            max_iterations=5,
        )

        result_obj = asyncio.run(self.think_and_act(task))

        try:
            report = json.loads(result_obj.output)
        except:
            report = {
                "verified": result_obj.success,
                "confidence": 50,
                "feedback": result_obj.output,
                "recommendation": "accept" if result_obj.success else "request_changes",
            }

        return report

    def validate_solution(self, solution: str, test_cases: str) -> Dict[str, Any]:
        """Validate a solution against test cases.

        Args:
            solution: Solution/code to validate
            test_cases: Test cases to validate against

        Returns:
            Validation report
        """
        import asyncio

        task = Task(
            description=f"Validate this solution against test cases:\nSolution:\n{solution}\n\nTest Cases:\n{test_cases}",
            constraints=["Check all test cases", "Report passes/failures"],
            max_iterations=5,
        )

        result = asyncio.run(self.think_and_act(task))

        return {
            "valid": result.success,
            "report": result.output,
            "reasoning": result.reasoning_trace,
        }
