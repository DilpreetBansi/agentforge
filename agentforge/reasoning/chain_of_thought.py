"""Chain-of-Thought reasoning strategy."""

from typing import Any, Dict, List
import json


class ChainOfThoughtReasoner:
    """Implements Chain-of-Thought reasoning."""

    def __init__(self, llm_provider: Any):
        """Initialize CoT reasoner.

        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider

    def reason(self, problem: str, num_samples: int = 1) -> Dict[str, Any]:
        """Perform CoT reasoning on a problem.

        Args:
            problem: Problem to reason about
            num_samples: Number of reasoning samples (for self-consistency)

        Returns:
            Reasoning result with answer
        """
        import asyncio

        async def async_reason():
            reasoning_traces = []
            final_answers = []

            for i in range(num_samples):
                prompt = f"""Let's think through this step by step.

Problem: {problem}

Step 1: Understand the problem
Step 2: Identify key information
Step 3: Plan the solution
Step 4: Execute the plan
Step 5: Verify the answer

Provide detailed reasoning for each step, then give the final answer."""

                response = await self.llm_provider.generate(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )

                reasoning_traces.append(response.get("thinking", response.get("response", "")))
                final_answers.append(response.get("response", ""))

            # Extract and combine answers
            return {
                "reasoning_traces": reasoning_traces,
                "final_answers": final_answers,
                "primary_answer": final_answers[0] if final_answers else "",
                "num_samples": num_samples,
            }

        return asyncio.run(async_reason())

    def self_consistency(self, problem: str, num_samples: int = 5) -> Dict[str, Any]:
        """Use self-consistency voting to find best answer.

        Args:
            problem: Problem to solve
            num_samples: Number of reasoning samples

        Returns:
            Most consistent answer with confidence
        """
        result = self.reason(problem, num_samples)

        # Simple voting - group similar answers
        from collections import Counter

        answer_counts = Counter(result["final_answers"])
        most_common = answer_counts.most_common(1)

        if most_common:
            best_answer, count = most_common[0]
            confidence = count / num_samples
        else:
            best_answer = result["primary_answer"]
            confidence = 0.5

        return {
            "answer": best_answer,
            "confidence": confidence,
            "vote_counts": dict(answer_counts),
            "reasoning_traces": result["reasoning_traces"],
        }


def format_cot_prompt(problem: str) -> str:
    """Format a problem for CoT reasoning.

    Args:
        problem: Problem statement

    Returns:
        Formatted prompt for CoT
    """
    return f"""Please solve this step-by-step.

{problem}

Let's think about this carefully:
1. What is being asked?
2. What information is given?
3. What is the solution approach?
4. What is the final answer?

Provide your detailed reasoning."""
