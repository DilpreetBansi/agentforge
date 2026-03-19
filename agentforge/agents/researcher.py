"""Research and information gathering agent."""

from typing import Any, List, Dict
from agentforge.core.agent import Agent, ToolDefinition
from agentforge.core.task import Task
from agentforge.tools.web_search import search_web


class ResearcherAgent(Agent):
    """Agent specialized in research and information gathering."""

    def __init__(self, llm_provider: Any):
        """Initialize researcher agent."""
        tools = [
            ToolDefinition(
                name="search_web",
                description="Search the web for information",
                func=search_web,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 5,
                    },
                },
            ),
        ]

        super().__init__(
            name="researcher",
            role="Research and information synthesis specialist",
            llm_provider=llm_provider,
            tools=tools,
            system_prompt="""You are a research specialist. Your job is to:
1. Search for relevant information
2. Evaluate source credibility
3. Synthesize findings into coherent insights
4. Provide citations and references
5. Answer questions comprehensively

When you have enough information, provide a detailed answer with sources.""",
        )

    def research_topic(self, topic: str) -> Dict[str, Any]:
        """Research a topic and synthesize findings.

        Args:
            topic: Topic to research

        Returns:
            Research findings with citations
        """
        import asyncio

        task = Task(
            description=f"Research this topic thoroughly: {topic}",
            constraints=[
                "Search for multiple perspectives",
                "Cite all sources",
                "Provide balanced view",
            ],
            max_iterations=10,
        )

        result = asyncio.run(self.think_and_act(task))

        return {
            "topic": topic,
            "findings": result.output,
            "reasoning_trace": result.reasoning_trace,
            "success": result.success,
        }

    def answer_question(self, question: str, context: str = "") -> str:
        """Answer a question with research.

        Args:
            question: Question to answer
            context: Optional context

        Returns:
            Answer with sources
        """
        import asyncio

        prompt = f"Answer this question with detailed research: {question}"
        if context:
            prompt += f"\n\nContext: {context}"

        task = Task(
            description=prompt,
            constraints=["Cite sources", "Be comprehensive"],
            max_iterations=8,
        )

        result = asyncio.run(self.think_and_act(task))
        return result.output

    def compare_options(self, options: List[str], criteria: str = "") -> Dict[str, Any]:
        """Compare multiple options.

        Args:
            options: Options to compare
            criteria: Comparison criteria

        Returns:
            Comparison analysis
        """
        import asyncio

        prompt = f"Compare these options: {', '.join(options)}"
        if criteria:
            prompt += f"\n\nComparison criteria: {criteria}"

        task = Task(
            description=prompt,
            constraints=["Use research", "Be objective"],
            max_iterations=10,
        )

        result = asyncio.run(self.think_and_act(task))

        return {
            "options": options,
            "analysis": result.output,
            "reasoning": result.reasoning_trace,
        }
