"""
Core Autonomous Agent — the main loop that orchestrates:
    PLAN → EXECUTE → REFLECT → (iterate?) → SYNTHESIZE
"""
import os
import re
from datetime import datetime
from typing import Callable, Optional

from .config import Config
from .providers import get_provider
from .providers.base import BaseLLMProvider
from .planner import Planner
from .executor import Executor
from .reflector import Reflector
from .memory import WorkingMemory
from .prompts import (
    get_system_prompt, get_planning_prompt, get_report_prompt,
    TITLE_PROMPT,
)


class AutonomousAgent:
    """
    The Autonomous Research & Solution Architect Agent.
    
    Given a goal, this agent will autonomously:
    1. Plan research tasks
    2. Execute searches and analyze findings
    3. Reflect on quality and iterate if needed
    4. Generate a comprehensive report
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.memory = WorkingMemory()
        self._log_callback: Optional[Callable] = None
        self.compact = self.config.small_model_mode

        # Initialize LLM provider
        provider_name = self.config.provider_name
        provider_config = self.config.provider_config
        self.llm = get_provider(provider_name, **provider_config)

        # Initialize sub-agents with config-aware settings
        self.planner = Planner(self.llm)
        self.executor = Executor(
            self.llm,
            max_search_results=self.config.max_search_results,
            max_pages=self.config.max_pages_to_extract,
            max_content_chars=self.config.max_content_chars,
            max_analysis_tokens=self.config.max_analysis_tokens,
            compact_mode=self.compact,
        )
        self.reflector = Reflector(self.llm)

        # Wire up logging
        self.executor.set_logger(self._log)

    def set_log_callback(self, callback: Callable):
        """Set a callback function for real-time logging (for UI/CLI)."""
        self._log_callback = callback

    def _log(self, phase: str, message: str):
        """Internal logging — writes to memory and optional callback."""
        self.memory.add_log(phase, message)
        if self._log_callback:
            self._log_callback(phase, message)

    def run(self, goal: str) -> str:
        """
        Run the autonomous research loop.
        
        Args:
            goal: The research goal / question from the user
            
        Returns:
            The final markdown report as a string
        """
        self.memory.reset(goal)
        mode_label = "COMPACT" if self.compact else "FULL"
        self._log("init", f"🚀 Autonomous Agent activated")
        self._log("init", f"🤖 Provider: {self.llm}")
        self._log("init", f"⚙️ Mode: {mode_label}")
        self._log("init", f"🎯 Goal: {goal}")

        max_iterations = self.config.max_iterations
        depth = self.config.research_depth

        # ═══════════════════════════════════════════════════════════════
        # PHASE 1: PLANNING
        # ═══════════════════════════════════════════════════════════════
        self.memory.status = "planning"
        self._log("plan", "📋 PHASE 1: PLANNING — Breaking down the goal...")

        queries = self.planner.create_plan(goal, depth=depth, compact=self.compact)
        self.memory.plan = queries

        self._log("plan", f"✅ Plan created with {len(queries)} research tasks:")
        for i, q in enumerate(queries, 1):
            self._log("plan", f"   {i}. {q}")

        # ═══════════════════════════════════════════════════════════════
        # PHASE 2-3: EXECUTE + REFLECT LOOP
        # ═══════════════════════════════════════════════════════════════
        all_queries = list(queries)
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            self.memory.iteration = iteration
            self.memory.status = "researching"

            self._log("execute", f"\n🔄 ITERATION {iteration}/{max_iterations}")

            # Execute pending queries
            pending = [q for q in all_queries if q not in self.memory.completed_queries]
            if not pending:
                self._log("execute", "All queries completed.")
                break

            self._log("execute", f"📋 PHASE 2: EXECUTING — {len(pending)} tasks remaining...")

            for i, query in enumerate(pending, 1):
                self._log("execute", f"\n── Task {i}/{len(pending)} ──")
                result = self.executor.execute_query(query)
                self.memory.add_finding(
                    query=result["query"],
                    analysis=result["analysis"],
                    sources=result["sources"],
                )

            # Reflect
            self.memory.status = "reflecting"
            self._log("reflect", "\n🔍 PHASE 3: REFLECTING — Evaluating research quality...")

            research_summary = self.memory.get_findings_summary()
            reflection = self.reflector.evaluate(goal, research_summary,
                                                 compact=self.compact)

            self.memory.add_reflection(
                completeness=reflection["completeness"],
                depth=reflection["depth"],
                gaps=reflection["gaps"],
                verdict=reflection["verdict"],
            )

            self._log("reflect", f"   Completeness: {reflection['completeness']}/10")
            self._log("reflect", f"   Depth: {reflection['depth']}/10")
            self._log("reflect", f"   Gaps: {reflection['gaps']}")
            self._log("reflect", f"   Verdict: {reflection['verdict']}")

            # Should we continue?
            if self.reflector.should_continue(reflection, max_iterations, iteration):
                new_queries = reflection.get("additional_queries", [])
                if new_queries:
                    self._log("reflect", f"🔄 Agent decided to do MORE research:")
                    for q in new_queries:
                        self._log("reflect", f"   + {q}")
                        all_queries.append(q)
                else:
                    break
            else:
                self._log("reflect", "✅ Research quality is sufficient.")
                break

        # ═══════════════════════════════════════════════════════════════
        # PHASE 4: SYNTHESIZE
        # ═══════════════════════════════════════════════════════════════
        self.memory.status = "synthesizing"
        self._log("synthesize", "\n📝 PHASE 4: SYNTHESIZING — Generating final report...")

        report = self._generate_report(goal)
        self.memory.status = "complete"

        self._log("complete", "✅ Report generation complete!")
        self._log("complete", f"📊 Total findings: {len(self.memory.findings)}")
        self._log("complete", f"🔄 Total iterations: {iteration}")

        return report

    def _generate_report(self, goal: str) -> str:
        """Generate the final comprehensive report."""
        system_prompt = get_system_prompt(compact=self.compact)

        # First generate a title
        title_messages = [
            {"role": "user", "content": TITLE_PROMPT.format(goal=goal)},
        ]
        title = self.llm.generate(title_messages, temperature=0.5, max_tokens=100).strip()
        title = title.strip('"\'')

        # Generate the full report
        all_findings = self.memory.get_findings_summary()
        report_prompt = get_report_prompt(
            goal=goal,
            all_findings=all_findings,
            title=title,
            compact=self.compact,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": report_prompt},
        ]

        max_tokens = self.config.max_report_tokens
        report = self.llm.generate(messages, temperature=0.4, max_tokens=max_tokens)
        return report

    def save_report(self, report: str, filename: str = None) -> str:
        """Save the report to a markdown file in the outputs directory."""
        output_dir = self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)

        if not filename:
            # Generate filename from goal
            safe_name = re.sub(r'[^\w\s-]', '', self.memory.goal)
            safe_name = re.sub(r'\s+', '_', safe_name)[:60]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.md"

        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

        self._log("save", f"💾 Report saved to: {filepath}")
        return filepath

    def get_status(self) -> dict:
        """Get current agent state (for UI)."""
        return self.memory.get_state_dict()
