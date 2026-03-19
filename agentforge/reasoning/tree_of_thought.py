"""Tree-of-Thought reasoning strategy."""

from typing import Any, Dict, List, Optional
import json
from dataclasses import dataclass
from collections import deque


@dataclass
class ThoughtNode:
    """Node in the tree of thoughts."""

    thought: str
    parent: Optional["ThoughtNode"] = None
    children: List["ThoughtNode"] = None
    value: float = 0.0  # Quality score
    depth: int = 0

    def __post_init__(self):
        """Initialize children list."""
        if self.children is None:
            self.children = []

    def add_child(self, thought: str) -> "ThoughtNode":
        """Add a child thought."""
        child = ThoughtNode(thought, parent=self, depth=self.depth + 1)
        self.children.append(child)
        return child


class TreeOfThoughtReasoner:
    """Implements Tree-of-Thought reasoning."""

    def __init__(self, llm_provider: Any):
        """Initialize ToT reasoner.

        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider

    async def reason(
        self,
        problem: str,
        max_depth: int = 3,
        branching_factor: int = 3,
        search_type: str = "bfs",
    ) -> Dict[str, Any]:
        """Perform Tree-of-Thought reasoning.

        Args:
            problem: Problem to solve
            max_depth: Maximum tree depth
            branching_factor: Number of child thoughts per node
            search_type: "bfs" or "dfs"

        Returns:
            Best solution found
        """
        # Create root node
        root = ThoughtNode(thought=problem, depth=0)

        # Expand tree
        if search_type == "bfs":
            await self._expand_bfs(root, max_depth, branching_factor)
        else:
            await self._expand_dfs(root, max_depth, branching_factor)

        # Find best path
        best_path = self._find_best_path(root)

        return {
            "solution": best_path[-1].thought if best_path else problem,
            "path": [node.thought for node in best_path],
            "reasoning_depth": len(best_path) - 1,
            "max_depth": max_depth,
        }

    async def _expand_bfs(
        self, root: ThoughtNode, max_depth: int, branching_factor: int
    ) -> None:
        """Expand tree using BFS."""
        queue = deque([root])
        visited = {id(root)}

        while queue:
            node = queue.popleft()

            if node.depth >= max_depth:
                continue

            # Generate child thoughts
            children = await self._generate_thoughts(node.thought, branching_factor)

            for child_thought in children:
                child = node.add_child(child_thought)
                child.value = await self._evaluate_thought(child_thought)

                if id(child) not in visited:
                    visited.add(id(child))
                    queue.append(child)

    async def _expand_dfs(
        self, root: ThoughtNode, max_depth: int, branching_factor: int
    ) -> None:
        """Expand tree using DFS."""

        async def dfs(node: ThoughtNode):
            if node.depth >= max_depth:
                return

            children = await self._generate_thoughts(node.thought, branching_factor)

            for child_thought in children:
                child = node.add_child(child_thought)
                child.value = await self._evaluate_thought(child_thought)
                await dfs(child)

        await dfs(root)

    async def _generate_thoughts(self, parent_thought: str, num: int) -> List[str]:
        """Generate child thoughts from parent."""
        prompt = f"""Given this thought: {parent_thought}

Generate {num} alternative next steps or refinements.
Format as JSON list:
["thought1", "thought2", "thought3"]"""

        response = await self.llm_provider.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )

        try:
            thoughts = json.loads(response.get("response", "[]"))
            return thoughts[:num]
        except:
            return [parent_thought]

    async def _evaluate_thought(self, thought: str) -> float:
        """Evaluate quality of a thought."""
        prompt = f"""Rate this thought on a scale of 0-10 in terms of being a good step toward solving a problem.

Thought: {thought}

Response with just a number 0-10."""

        response = await self.llm_provider.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        try:
            score = float(response.get("response", "5").strip().split()[0])
            return min(10.0, max(0.0, score))
        except:
            return 5.0

    @staticmethod
    def _find_best_path(root: ThoughtNode) -> List[ThoughtNode]:
        """Find best path from root to leaf."""
        if not root.children:
            return [root]

        # Use greedy approach: always pick best child
        path = [root]
        current = root

        while current.children:
            best_child = max(current.children, key=lambda x: x.value)
            path.append(best_child)
            current = best_child

        return path


def format_tot_prompt(problem: str, num_thoughts: int = 3) -> str:
    """Format a problem for ToT reasoning.

    Args:
        problem: Problem statement
        num_thoughts: Number of parallel thoughts

    Returns:
        Formatted prompt for ToT
    """
    return f"""Think about this problem in {num_thoughts} different ways.

{problem}

For each perspective, provide:
1. Key insight
2. Reasoning
3. Next step

Then synthesize into a final solution."""
