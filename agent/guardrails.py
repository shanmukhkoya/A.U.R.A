"""
Guardrails — Middleware to protect the agent from hallucinations and formatting errors.
"""
import re
from typing import Optional, Callable
from .providers.base import BaseLLMProvider

class Guardrails:
    """
    Enforces format constraints and runs hallucination checks to ensure
    the autonomous agent produces reliable, grounded outputs.
    """
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm
        self._log_callback: Optional[Callable] = None

    def set_logger(self, logger: Callable):
        self._log_callback = logger

    def _log(self, phase: str, message: str):
        if self._log_callback:
            self._log_callback(phase, message)

    def validate_reflection_format(self, text: str) -> bool:
        """
        Check if the LLM output contains the required reflection keys.
        Small models often forget these, breaking the regex parser.
        """
        required_keys = ["COMPLETENESS:", "DEPTH:", "VERDICT:"]
        missing = [key for key in required_keys if key.lower() not in text.lower()]
        
        if missing:
            self._log("guardrail", f"⚠️ Format Guardrail triggered: Missing keys {missing}")
            return False
        return True

    def check_hallucination(self, report: str, context: str, compact: bool = False) -> bool:
        """
        Groundedness Check: Asks the LLM to verify if the report contains
        hallucinated facts not present in the web context.
        """
        self._log("guardrail", "🛡️ Running Hallucination / Groundedness check...")
        
        # Truncate context to save tokens on the check
        max_context = 3000 if compact else 8000
        safe_context = context[:max_context]
        
        prompt = (
            "You are a strict fact-checker.\n"
            "Review the following final report and compare it to the Source Context.\n\n"
            f"--- SOURCE CONTEXT ---\n{safe_context}\n\n"
            f"--- FINAL REPORT ---\n{report}\n\n"
            "Does the final report contain any massive hallucinations or completely fabricated "
            "facts that contradict the source context? Ignore minor formatting differences.\n"
            "Reply EXACTLY with 'PASS' if grounded, or 'FAIL' if heavily hallucinated."
        )
        
        messages = [{"role": "user", "content": prompt}]
        response = self.llm.generate(messages, temperature=0.0, max_tokens=10)
        
        # If the LLM says fail, we flag it.
        if "FAIL" in response.upper():
            self._log("guardrail", "❌ Hallucination detected! Report may be ungrounded.")
            return False
            
        self._log("guardrail", "✅ Groundedness check passed.")
        return True
