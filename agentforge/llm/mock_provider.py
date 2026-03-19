"""Mock LLM provider for testing - NO MODEL REQUIRED."""

from typing import Any, Dict, List, Optional
import random
import json
from agentforge.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing without a real model."""

    def __init__(self, **kwargs):
        """Initialize mock provider."""
        super().__init__(**kwargs)
        self.call_count = 0

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate mock response.

        Args:
            messages: Conversation messages
            tools: Available tools
            temperature: Temperature (ignored)
            max_tokens: Max tokens (ignored)
            **kwargs: Additional arguments

        Returns:
            Mock response
        """
        self.call_count += 1

        # Extract the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # Generate contextual mock responses
        if "fibonacci" in user_message.lower():
            response = self._mock_fibonacci(user_message)
        elif "fizzbuzz" in user_message.lower():
            response = self._mock_fizzbuzz(user_message)
        elif "sum" in user_message.lower() or "add" in user_message.lower():
            response = self._mock_sum(user_message)
        elif "palindrome" in user_message.lower():
            response = self._mock_palindrome(user_message)
        elif "merge" in user_message.lower():
            response = self._mock_merge(user_message)
        elif "decompose" in user_message.lower():
            response = self._mock_decompose(user_message)
        elif "review" in user_message.lower():
            response = self._mock_review(user_message)
        elif "research" in user_message.lower():
            response = self._mock_research(user_message)
        else:
            response = self._mock_generic_response(user_message)

        return {
            "response": response,
            "thinking": "Mock reasoning process",
            "done": True,
            "tool_calls": [],
        }

    @staticmethod
    def _mock_fibonacci(message: str) -> str:
        """Mock fibonacci implementation."""
        return """def fibonacci(n):
    '''Return the nth Fibonacci number.'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test cases
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(5) == 5
assert fibonacci(10) == 55

SOLUTION_COMPLETE"""

    @staticmethod
    def _mock_fizzbuzz(message: str) -> str:
        """Mock FizzBuzz implementation."""
        return """def fizzbuzz(n):
    '''Print FizzBuzz sequence.'''
    for i in range(1, n+1):
        output = ""
        if i % 3 == 0:
            output += "Fizz"
        if i % 5 == 0:
            output += "Buzz"
        print(output or i)

# Test
fizzbuzz(15)

SOLUTION_COMPLETE"""

    @staticmethod
    def _mock_sum(message: str) -> str:
        """Mock sum function."""
        return """def add_numbers(a, b):
    '''Return the sum of two numbers.'''
    return a + b

# Test cases
assert add_numbers(2, 3) == 5
assert add_numbers(-1, 1) == 0
assert add_numbers(100, 200) == 300

SOLUTION_COMPLETE"""

    @staticmethod
    def _mock_palindrome(message: str) -> str:
        """Mock palindrome checker."""
        return """def is_palindrome(s):
    '''Check if string is a palindrome.'''
    s = s.lower().replace(' ', '')
    return s == s[::-1]

# Test cases
assert is_palindrome('racecar') == True
assert is_palindrome('hello') == False
assert is_palindrome('A man a plan a canal Panama') == True

SOLUTION_COMPLETE"""

    @staticmethod
    def _mock_merge(message: str) -> str:
        """Mock merge sorted lists."""
        return """def merge_sorted_lists(list1, list2):
    '''Merge two sorted lists.'''
    result = []
    i, j = 0, 0

    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1

    result.extend(list1[i:])
    result.extend(list2[j:])
    return result

# Test cases
assert merge_sorted_lists([1,3,5], [2,4,6]) == [1,2,3,4,5,6]
assert merge_sorted_lists([], [1,2]) == [1,2]

SOLUTION_COMPLETE"""

    @staticmethod
    def _mock_decompose(message: str) -> str:
        """Mock task decomposition."""
        decomposition = {
            "subtasks": [
                {
                    "id": "task_1",
                    "description": "Understand requirements",
                    "agent": "planner",
                    "dependencies": [],
                    "estimated_iterations": 2,
                },
                {
                    "id": "task_2",
                    "description": "Write implementation",
                    "agent": "coder",
                    "dependencies": ["task_1"],
                    "estimated_iterations": 5,
                },
                {
                    "id": "task_3",
                    "description": "Test solution",
                    "agent": "executor",
                    "dependencies": ["task_2"],
                    "estimated_iterations": 3,
                },
                {
                    "id": "task_4",
                    "description": "Code review",
                    "agent": "reviewer",
                    "dependencies": ["task_2"],
                    "estimated_iterations": 2,
                },
            ],
            "critical_path": ["task_1", "task_2", "task_4"],
            "reasoning": "Standard software development workflow",
        }
        return json.dumps(decomposition)

    @staticmethod
    def _mock_review(message: str) -> str:
        """Mock code review."""
        review = {
            "quality_score": 85,
            "issues": [
                {
                    "severity": "minor",
                    "type": "style",
                    "location": "line 5",
                    "description": "Missing docstring",
                    "suggestion": "Add docstring to function",
                }
            ],
            "overall_assessment": "Good implementation with minor style issues",
            "recommendation": "approve",
        }
        return json.dumps(review)

    @staticmethod
    def _mock_research(message: str) -> str:
        """Mock research response."""
        research = {
            "findings": "Research shows that distributed systems require careful consideration of consistency, availability, and partition tolerance (CAP theorem). Key findings include...",
            "sources": [
                "https://example.com/paper1",
                "https://example.com/paper2",
            ],
            "summary": "Topic is important and well-studied with proven approaches.",
        }
        return json.dumps(research)

    @staticmethod
    def _mock_generic_response(message: str) -> str:
        """Mock generic response."""
        responses = [
            "I understand the task. Let me break it down into steps and solve it systematically.",
            "This is a complex problem. I'll analyze it carefully and provide a solution.",
            "I have a clear understanding of what needs to be done. Let me proceed with the implementation.",
            "The task is clear. I'll work through this methodically to provide the best solution.",
        ]
        return random.choice(responses)
