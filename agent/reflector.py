"""Reflector — self-evaluation and quality control loop."""
import re
from typing import Dict, List, Tuple
from .providers.base import BaseLLMProvider
from .prompts import get_reflection_prompt, get_system_prompt


class Reflector:
    """
    Evaluates research quality and decides whether to iterate.
    This is what makes the agent truly autonomous — it can recognize
    gaps in its own work and plan additional research.
    """

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def evaluate(self, goal: str, research_summary: str,
                 compact: bool = False) -> Dict:
        """
        Evaluate the current research and decide whether to continue.
        
        Returns dict with:
            completeness: int (1-10)
            depth: int (1-10)
            gaps: str
            verdict: 'MORE' or 'SUFFICIENT'
            additional_queries: list of new queries if MORE
        """
        prompt = get_reflection_prompt(goal, research_summary, compact=compact)

        messages = [
            {"role": "system", "content": get_system_prompt(compact=compact)},
            {"role": "user", "content": prompt},
        ]

        max_tokens = 300 if compact else 500
        response = self.llm.generate(messages, temperature=0.2, max_tokens=max_tokens)

        return self._parse_reflection(response)

    def _parse_reflection(self, response: str) -> Dict:
        """Parse the structured reflection response."""
        result = {
            "completeness": 5,
            "depth": 5,
            "gaps": "Unable to parse",
            "verdict": "SUFFICIENT",
            "additional_queries": [],
            "raw": response,
        }

        try:
            # Extract scores
            comp_match = re.search(r"COMPLETENESS:\s*(\d+)", response, re.IGNORECASE)
            if comp_match:
                result["completeness"] = min(int(comp_match.group(1)), 10)

            depth_match = re.search(r"DEPTH:\s*(\d+)", response, re.IGNORECASE)
            if depth_match:
                result["depth"] = min(int(depth_match.group(1)), 10)

            # Extract gaps
            gaps_match = re.search(r"GAPS:\s*(.+?)(?=VERDICT:|$)", response, re.IGNORECASE | re.DOTALL)
            if gaps_match:
                result["gaps"] = gaps_match.group(1).strip()

            # Extract verdict
            verdict_match = re.search(r"VERDICT:\s*(MORE|SUFFICIENT)", response, re.IGNORECASE)
            if verdict_match:
                result["verdict"] = verdict_match.group(1).upper()

            # Extract additional queries
            queries_match = re.search(
                r"ADDITIONAL_QUERIES:\s*(.+?)$", response, re.IGNORECASE | re.DOTALL
            )
            if queries_match:
                queries_text = queries_match.group(1).strip()
                if queries_text.lower() != "none":
                    queries = [
                        line.strip().lstrip("0123456789.-) ").strip()
                        for line in queries_text.split("\n")
                        if line.strip() and line.strip().lower() != "none"
                    ]
                    result["additional_queries"] = queries[:2]

        except Exception:
            pass  # Use defaults if parsing fails

        return result

    def should_continue(self, reflection: Dict, max_iterations: int, current_iteration: int) -> bool:
        """Decide if the agent should do more research."""
        if current_iteration >= max_iterations:
            return False

        if reflection["verdict"] == "MORE" and reflection.get("additional_queries"):
            avg_score = (reflection["completeness"] + reflection["depth"]) / 2
            # Only continue if quality is below threshold
            return avg_score < 8

        return False
