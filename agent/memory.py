"""Working Memory — manages the agent's context across the autonomous loop."""
from typing import List, Dict, Optional
from datetime import datetime


class WorkingMemory:
    """
    Maintains the agent's working state throughout the research cycle.
    Tracks: goal, plan, findings, reflections, and the final report.
    """

    def __init__(self):
        self.goal: str = ""
        self.started_at: str = ""
        self.plan: List[str] = []
        self.completed_queries: List[str] = []
        self.findings: List[Dict[str, str]] = []
        self.reflections: List[Dict] = []
        self.additional_queries: List[str] = []
        self.iteration: int = 0
        self.status: str = "idle"
        self.log: List[Dict[str, str]] = []

    def reset(self, goal: str):
        """Reset memory for a new research goal."""
        self.__init__()
        self.goal = goal
        self.started_at = datetime.now().isoformat()
        self.status = "initialized"

    def add_log(self, phase: str, message: str):
        """Add a log entry."""
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "phase": phase,
            "message": message,
        }
        self.log.append(entry)

    def add_finding(self, query: str, analysis: str, sources: List[str] = None):
        """Add a research finding."""
        self.findings.append({
            "query": query,
            "analysis": analysis,
            "sources": sources or [],
            "iteration": self.iteration,
        })
        self.completed_queries.append(query)

    def add_reflection(self, completeness: int, depth: int, gaps: str, verdict: str):
        """Add a reflection result."""
        self.reflections.append({
            "iteration": self.iteration,
            "completeness": completeness,
            "depth": depth,
            "gaps": gaps,
            "verdict": verdict,
        })

    def get_findings_summary(self) -> str:
        """Get a formatted summary of all findings for the LLM."""
        if not self.findings:
            return "No findings yet."

        parts = []
        for i, f in enumerate(self.findings, 1):
            sources_str = "\n".join(f["sources"]) if f["sources"] else "N/A"
            parts.append(
                f"### Research Task {i}: {f['query']}\n"
                f"{f['analysis']}\n"
                f"**Sources:** {sources_str}\n"
            )
        return "\n".join(parts)

    def get_state_dict(self) -> dict:
        """Get the full state as a dictionary (for serialization / UI)."""
        return {
            "goal": self.goal,
            "started_at": self.started_at,
            "iteration": self.iteration,
            "status": self.status,
            "plan": self.plan,
            "completed_queries": self.completed_queries,
            "findings_count": len(self.findings),
            "reflections": self.reflections,
            "log": self.log,
        }
