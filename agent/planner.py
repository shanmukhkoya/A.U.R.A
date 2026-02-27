"""Planner — breaks down goals into research sub-tasks."""
from typing import List
from .providers.base import BaseLLMProvider
from .prompts import get_planning_prompt, get_system_prompt


class Planner:
    """Decomposes a high-level goal into specific research queries."""

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def create_plan(self, goal: str, depth: str = "detailed",
                    num_tasks: int = 5, compact: bool = False) -> List[str]:
        """
        Generate a list of research queries from the goal.
        
        Args:
            goal: The user's research goal
            depth: Research depth — 'quick' (3), 'detailed' (5), 'exhaustive' (8)
            num_tasks: Number of research queries to generate
            compact: Use compact prompts for small models
        """
        depth_map = {"quick": 3, "detailed": 5, "exhaustive": 8}
        num_tasks = depth_map.get(depth, num_tasks)

        prompt = get_planning_prompt(goal, depth, num_tasks, compact=compact)

        messages = [
            {"role": "system", "content": get_system_prompt(compact=compact)},
            {"role": "user", "content": prompt},
        ]

        max_tokens = 300 if compact else 500
        response = self.llm.generate(messages, temperature=0.4, max_tokens=max_tokens)

        # Parse queries — one per line, filter empty lines
        queries = [
            line.strip().lstrip("0123456789.-) ").strip()
            for line in response.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        # Remove any accidental duplicates
        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen and len(q) > 10:
                seen.add(q.lower())
                unique_queries.append(q)

        return unique_queries[:num_tasks]
