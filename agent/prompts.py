"""
Prompt templates for the Autonomous Agent.
All prompts are designed to work reliably with both small local models and large frontier models.
Compact variants are provided for small models to reduce token usage.
"""

# ─────────────────────────────────────────────────────────────────────
# SYSTEM IDENTITY
# ─────────────────────────────────────────────────────────────────────
AGENT_SYSTEM_PROMPT = """You are an Autonomous Research & Solution Architect Agent.
Your expertise covers Contact Center technologies, VoIP, CTI integrations, CCaaS platforms, PBX systems, telephony protocols, and enterprise communications.

You operate autonomously by:
1. PLANNING — Breaking down complex goals into research tasks
2. RESEARCHING — Searching the web and extracting relevant information
3. ANALYZING — Reasoning about findings, comparing solutions, identifying trade-offs
4. REFLECTING — Evaluating your own work quality and filling gaps
5. SYNTHESIZING — Producing comprehensive, actionable reports

You are thorough, objective, and always provide evidence-based recommendations."""

AGENT_SYSTEM_PROMPT_COMPACT = """You are a research agent. Analyze information and provide clear, factual responses. Be concise."""


# ─────────────────────────────────────────────────────────────────────
# PLANNING PHASE
# ─────────────────────────────────────────────────────────────────────
PLANNING_PROMPT = """You are a research planner. Given a user's goal, break it down into specific research tasks.

USER'S GOAL:
{goal}

RESEARCH DEPTH: {depth}

Create a research plan with {num_tasks} focused search queries. Each query should target a different aspect of the goal.

RULES:
- Each query should be specific and searchable on the web
- Cover different angles: technical, comparison, best practices, challenges, pricing
- Queries should build on each other logically
- For Contact Center/VoIP topics, include vendor-specific and protocol-specific queries

Return ONLY the queries, one per line. No numbering, no bullets, no explanations.
Example format:
query one text here
query two text here
query three text here"""

PLANNING_PROMPT_COMPACT = """Break this goal into {num_tasks} web search queries. Each query targets a different aspect.

GOAL: {goal}
DEPTH: {depth}

Return ONLY the queries, one per line. No numbering or explanations.
Example:
query one
query two"""


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS PHASE
# ─────────────────────────────────────────────────────────────────────
ANALYSIS_PROMPT = """You are a research analyst specializing in Contact Center and enterprise communications.

RESEARCH QUERY: {query}

SEARCH RESULTS:
{search_results}

WEB CONTENT:
{web_content}

Analyze the above information and provide:
1. KEY FINDINGS — The most important facts, specifications, and data points
2. TECHNICAL DETAILS — Relevant protocols, APIs, integration methods, architectures
3. VENDOR INSIGHTS — Products, platforms, pricing if available
4. GAPS — What information is missing or needs further research

Keep your analysis factual and concise (max 400 words). Cite sources when possible."""

ANALYSIS_PROMPT_COMPACT = """Analyze these search results for the query below. Provide key findings in 150 words max.

QUERY: {query}

RESULTS:
{search_results}

CONTENT:
{web_content}

Write a brief factual summary of the key findings. Be concise."""


def get_analysis_prompt(query, search_results, web_content, compact=False):
    """Get the appropriate analysis prompt based on model mode."""
    if compact:
        return ANALYSIS_PROMPT_COMPACT.format(
            query=query, search_results=search_results, web_content=web_content
        )
    return ANALYSIS_PROMPT.format(
        query=query, search_results=search_results, web_content=web_content
    )


# ─────────────────────────────────────────────────────────────────────
# REFLECTION PHASE
# ─────────────────────────────────────────────────────────────────────
REFLECTION_PROMPT = """You are a quality reviewer evaluating research completeness.

ORIGINAL GOAL:
{goal}

RESEARCH COMPLETED SO FAR:
{research_summary}

Evaluate the research quality:
1. COMPLETENESS — Does the research fully address the user's goal? (Score 1-10)
2. DEPTH — Are there enough technical details and specifics? (Score 1-10)
3. GAPS — What critical information is still missing?
4. VERDICT — Should we do MORE research or is this SUFFICIENT?

Respond in this EXACT format:
COMPLETENESS: [score]
DEPTH: [score]
GAPS: [list any gaps, or "none"]
VERDICT: [MORE or SUFFICIENT]
ADDITIONAL_QUERIES: [if MORE, list 1-2 additional search queries, one per line. If SUFFICIENT, write "none"]"""

REFLECTION_PROMPT_COMPACT = """Rate this research for the goal below.

GOAL: {goal}

RESEARCH:
{research_summary}

Reply in EXACTLY this format:
COMPLETENESS: [1-10]
DEPTH: [1-10]
GAPS: [gaps or none]
VERDICT: [MORE or SUFFICIENT]
ADDITIONAL_QUERIES: [queries or none]"""


def get_reflection_prompt(goal, research_summary, compact=False):
    """Get the appropriate reflection prompt."""
    template = REFLECTION_PROMPT_COMPACT if compact else REFLECTION_PROMPT
    return template.format(goal=goal, research_summary=research_summary)


# ─────────────────────────────────────────────────────────────────────
# REPORT GENERATION
# ─────────────────────────────────────────────────────────────────────
REPORT_PROMPT = """You are a professional solution architect and technical writer.

USER'S ORIGINAL GOAL:
{goal}

ALL RESEARCH FINDINGS:
{all_findings}

Write a comprehensive, professional Markdown report. Structure it as follows:

# {title}

## Executive Summary
Brief overview of findings and recommendations (3-4 sentences).

## Background & Context
Why this matters and key context the reader needs.

## Key Findings
Organized by theme. Use tables for comparisons. Include specific technical details.

## Technical Architecture / Solution Design
If applicable, describe the recommended architecture, integration approach, or migration plan.
Include components, protocols, data flows.

## Comparison & Analysis
If comparing solutions/vendors, use a detailed comparison table.

## Recommendations
Numbered, actionable recommendations with justification.

## Implementation Considerations
Risks, challenges, prerequisites, timeline estimates.

## Conclusion
Final summary and next steps.

## Sources & References
List all sources from the research.

RULES:
- Be thorough and specific — this is a professional deliverable
- Use tables for comparisons
- Include technical specifics (protocols, APIs, versions)
- Provide actionable recommendations, not vague suggestions
- Write at least 1500 words for a detailed report"""

REPORT_PROMPT_COMPACT = """Write a research report based on the findings below.

GOAL: {goal}

FINDINGS:
{all_findings}

# {title}

## Summary
Brief overview (2-3 sentences).

## Key Findings
Main facts and insights.

## Recommendations
Top 3 actionable recommendations.

## Sources
List sources.

Keep the report under 600 words. Be direct and factual."""


def get_report_prompt(goal, all_findings, title, compact=False):
    """Get the appropriate report prompt."""
    template = REPORT_PROMPT_COMPACT if compact else REPORT_PROMPT
    return template.format(goal=goal, all_findings=all_findings, title=title)


# ─────────────────────────────────────────────────────────────────────
# TITLE GENERATION
# ─────────────────────────────────────────────────────────────────────
TITLE_PROMPT = """Generate a short, professional report title for this research goal:
"{goal}"

Return ONLY the title, nothing else. No quotes. Example:
CCaaS Migration Analysis: Avaya to Genesys Cloud"""


def get_system_prompt(compact=False):
    """Get the system prompt for the agent."""
    return AGENT_SYSTEM_PROMPT_COMPACT if compact else AGENT_SYSTEM_PROMPT


def get_planning_prompt(goal, depth, num_tasks, compact=False):
    """Get the planning prompt."""
    template = PLANNING_PROMPT_COMPACT if compact else PLANNING_PROMPT
    return template.format(goal=goal, depth=depth, num_tasks=num_tasks)
