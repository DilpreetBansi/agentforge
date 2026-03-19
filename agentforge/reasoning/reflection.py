"""Self-reflection and error recovery reasoning."""

from typing import Any, Dict, List, Optional
import json


class ReflectionReasoner:
    """Implements self-reflection for error recovery."""

    def __init__(self, llm_provider: Any):
        """Initialize reflection reasoner.

        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider

    async def reflect_on_error(
        self, problem: str, error: str, attempts: List[str]
    ) -> Dict[str, Any]:
        """Reflect on an error and generate correction.

        Args:
            problem: Original problem
            error: Error message
            attempts: Previous attempts

        Returns:
            Reflection and corrected approach
        """
        previous_attempts = "\n".join(
            [f"Attempt {i+1}: {attempt[:100]}..." for i, attempt in enumerate(attempts)]
        )

        prompt = f"""You failed to solve this problem. Analyze what went wrong.

Problem: {problem}

Error: {error}

Previous attempts:
{previous_attempts}

Reflection:
1. What was the root cause of failure?
2. What assumption was wrong?
3. What different approach could work?
4. How would you solve it differently?

Provide response as JSON:
{{
  "root_cause": "...",
  "wrong_assumption": "...",
  "new_approach": "...",
  "corrected_solution": "..."
}}"""

        response = await self.llm_provider.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        try:
            reflection = json.loads(response.get("response", "{}"))
        except:
            reflection = {
                "root_cause": error,
                "new_approach": response.get("response", "Try again"),
            }

        return reflection

    async def self_evaluate(self, solution: str, problem: str) -> Dict[str, Any]:
        """Self-evaluate a solution before submitting.

        Args:
            solution: Proposed solution
            problem: Original problem

        Returns:
            Evaluation and confidence score
        """
        prompt = f"""Evaluate this solution without running it.

Problem: {problem}

Solution:
{solution}

Evaluation:
1. Does it solve the problem correctly?
2. What edge cases might break it?
3. Is there a logical flaw?
4. How confident are you (0-100)?

Respond as JSON:
{{
  "correct": true/false,
  "confidence": 0-100,
  "edge_cases": ["..."],
  "logical_flaws": ["..."],
  "suggestions": ["..."]
}}"""

        response = await self.llm_provider.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        try:
            evaluation = json.loads(response.get("response", "{}"))
        except:
            evaluation = {
                "correct": True,
                "confidence": 50,
                "edge_cases": [],
            }

        return evaluation

    async def generate_corrections(
        self, error_analysis: Dict[str, Any], max_corrections: int = 3
    ) -> List[str]:
        """Generate possible corrections from error analysis.

        Args:
            error_analysis: Analysis of errors
            max_corrections: Maximum corrections to generate

        Returns:
            List of correction suggestions
        """
        prompt = f"""Based on this error analysis, generate corrected solutions.

Root cause: {error_analysis.get('root_cause', '')}
New approach: {error_analysis.get('new_approach', '')}

Generate {max_corrections} concrete solutions:"""

        response = await self.llm_provider.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )

        # Parse response into solutions
        solutions = response.get("response", "").split("\n")
        return [s.strip() for s in solutions if s.strip()][:max_corrections]

    async def verify_and_refine(
        self, solution: str, problem: str, test_results: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify solution and suggest refinements.

        Args:
            solution: Current solution
            problem: Original problem
            test_results: Optional test results

        Returns:
            Verification and refinement suggestions
        """
        context = f"Test results: {test_results}" if test_results else ""

        prompt = f"""Analyze this solution's quality and suggest improvements.

Problem: {problem}

Solution:
{solution}

{context}

Provide JSON response:
{{
  "quality_score": 0-100,
  "passes_requirements": true/false,
  "issues": ["..."],
  "refinements": ["..."],
  "is_final": true/false
}}"""

        response = await self.llm_provider.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )

        try:
            analysis = json.loads(response.get("response", "{}"))
        except:
            analysis = {
                "quality_score": 50,
                "passes_requirements": False,
                "is_final": False,
            }

        return analysis


def format_reflection_prompt(error_context: str) -> str:
    """Format a prompt for reflection.

    Args:
        error_context: Context about the error

    Returns:
        Formatted prompt for reflection
    """
    return f"""Reflect on what went wrong and how to improve.

Error context:
{error_context}

Analysis:
1. What was the mistake?
2. How can it be corrected?
3. What should be tried instead?
4. How confident are you in the correction?

Provide detailed reasoning."""
