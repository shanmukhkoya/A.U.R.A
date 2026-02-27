"""Evaluator module that acts as an LLM judge for autonomous agents' output."""
import re
from typing import Dict, List
from agent.providers.base import BaseLLMProvider

class Evaluator:
    def __init__(self, llm: BaseLLMProvider):
        """
        Initializes the LLM Evaluator (Judge).
        It's recommended to use a high-capacity model (e.g., GPT-4o or Claude 3.5 Sonnet) 
        as the evaluator for the most accurate benchmarking.
        """
        self.llm = llm

    def benchmark_report(self, question: str, expected_facts: List[str], generated_report: str) -> Dict[str, any]:
        """
        Scores a generated report based on Groundedness, Relevance, and Formatting.
        """
        facts_str = "\n".join([f"- {fact}" for fact in expected_facts])
        
        prompt = (
            "You are an expert AI evaluator benchmarking research reports.\n"
            "Below is a generated report responding to a specific research question.\n\n"
            f"QUESTION: {question}\n\n"
            f"EXPECTED FACTS TO COVER:\n{facts_str}\n\n"
            "=== GENERATED REPORT ===\n"
            f"{generated_report}\n"
            "========================\n\n"
            "Please evaluate the report on the following criteria. Format your response exactly as shown below.\n\n"
            "RELEVANCE: [Score 1-10] (Did it answer the question directly without drifting?)\n"
            "ACCURACY: [Score 1-10] (Did it cover the expected facts?)\n"
            "FORMATTING: [PASS/FAIL] (Is it a well-structured markdown document?)\n"
            "FEEDBACK: [1-2 sentences explaining the scores]"
        )

        messages = [{"role": "user", "content": prompt}]
        # Very low temperature for consistent judging
        response = self.llm.generate(messages, temperature=0.1, max_tokens=300)

        # Parse response using Regex
        return self._parse_evaluation(response)

    def _parse_evaluation(self, response: str) -> Dict[str, any]:
        """Extract scores from the Evaluator LLM response."""
        result = {
            "relevance": 0,
            "accuracy": 0,
            "formatting": "FAIL",
            "feedback": "Parsing failed.",
            "raw_response": response
        }

        try:
            rel_match = re.search(r"RELEVANCE:\s*(\d+)", response, re.IGNORECASE)
            if rel_match:
                result["relevance"] = int(rel_match.group(1))

            acc_match = re.search(r"ACCURACY:\s*(\d+)", response, re.IGNORECASE)
            if acc_match:
                result["accuracy"] = int(acc_match.group(1))

            fmt_match = re.search(r"FORMATTING:\s*(PASS|FAIL)", response, re.IGNORECASE)
            if fmt_match:
                result["formatting"] = fmt_match.group(1).upper()

            fb_match = re.search(r"FEEDBACK:\s*(.+)$", response, re.IGNORECASE | re.DOTALL)
            if fb_match:
                result["feedback"] = fb_match.group(1).strip()
        except Exception:
            pass

        return result
