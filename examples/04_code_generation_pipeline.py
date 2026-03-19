#!/usr/bin/env python3
"""
Example 4: Complete Code Generation Pipeline
Demonstrates: Code Generation -> Testing -> Review -> Verification
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge.agents.coder import CoderAgent, TestGeneratorAgent
from agentforge.agents.reviewer import ReviewerAgent
from agentforge.agents.verifier import VerifierAgent
from agentforge.llm.mock_provider import MockLLMProvider
from agentforge.tools.code_executor import execute_python_code


async def main():
    """Run code generation pipeline example."""
    print("=" * 70)
    print("AgentForge Example 4: Complete Code Generation Pipeline")
    print("=" * 70)
    print()

    # Initialize agents
    llm = MockLLMProvider()
    coder = CoderAgent(llm_provider=llm)
    test_gen = TestGeneratorAgent(llm_provider=llm)
    reviewer = ReviewerAgent(llm_provider=llm)
    verifier = VerifierAgent(llm_provider=llm)

    print("✓ Initialized all agents")
    print()

    # Define specification
    spec = """Write a function that finds the first recurring character in a string.

    Requirements:
    - Takes a string as input
    - Returns the first character that appears more than once
    - Returns None if no recurring character
    - Case-insensitive

    Test cases:
    - "hello" -> "l"
    - "programming" -> "r"
    - "abc" -> None
    - "aAbBcC" -> "a"
    """

    print("SPECIFICATION")
    print("=" * 70)
    print(spec)
    print("=" * 70)
    print()

    # Step 1: Code Generation
    print("STEP 1: Code Generation")
    print("-" * 70)
    code = coder.generate_code(spec)
    print(code[:400] + "..." if len(code) > 400 else code)
    print("-" * 70)
    print()

    # Step 2: Test Generation
    print("STEP 2: Test Generation")
    print("-" * 70)
    tests = test_gen.generate_tests(code, spec)
    print(tests[:300] + "..." if len(tests) > 300 else tests)
    print("-" * 70)
    print()

    # Step 3: Execute Code
    print("STEP 3: Code Execution Test")
    print("-" * 70)

    test_code = code + "\n\n# Quick test\nprint(first_recurring_char('hello'))"
    execution_result = execute_python_code(test_code)
    print(f"Execution result:\n{execution_result}")
    print("-" * 70)
    print()

    # Step 4: Code Review
    print("STEP 4: Code Review")
    print("-" * 70)
    review = reviewer.review_code(code, spec)

    if isinstance(review, dict):
        print(f"Quality Score: {review.get('quality_score', 'N/A')}/100")
        print(f"Recommendation: {review.get('recommendation', 'N/A')}")
        assessment = review.get("overall_assessment", "")
    else:
        print(review[:300])
        assessment = review

    print("-" * 70)
    print()

    # Step 5: Verification
    print("STEP 5: Result Verification")
    print("-" * 70)

    verification = verifier.verify_result(
        code, requirements=spec, success_criteria="Code passes all test cases"
    )

    if isinstance(verification, dict):
        print(f"Verified: {verification.get('verified', False)}")
        print(f"Confidence: {verification.get('confidence', 0)}%")
        print(f"Recommendation: {verification.get('recommendation', 'N/A')}")
    else:
        print(verification[:300])

    print("-" * 70)
    print()

    # Summary
    print("=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print("✓ Step 1: Code Generated")
    print("✓ Step 2: Tests Generated")
    print("✓ Step 3: Code Executed")
    print("✓ Step 4: Code Reviewed")
    print("✓ Step 5: Results Verified")
    print()
    print("Pipeline completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
