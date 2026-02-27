"""CLI Entry Point — run the agent from the command line with beautiful output."""
import sys
import os
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import AutonomousAgent
from agent.config import Config


# ─────────────────────────────────────────────────────────────────────
# ANSI Color Codes for beautiful terminal output
# ─────────────────────────────────────────────────────────────────────
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_MAGENTA = "\033[45m"

PHASE_COLORS = {
    "init": Colors.CYAN,
    "plan": Colors.BLUE,
    "execute": Colors.YELLOW,
    "search": Colors.DIM,
    "extract": Colors.DIM,
    "analyze": Colors.MAGENTA,
    "reflect": Colors.GREEN,
    "synthesize": Colors.CYAN,
    "complete": Colors.GREEN,
    "save": Colors.GREEN,
}


def print_banner():
    """Print a cool ASCII banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🤖  AUTONOMOUS RESEARCH & SOLUTION ARCHITECT AGENT  🤖 ║
    ║                                                          ║
    ║   Think  →  Plan  →  Research  →  Reflect  →  Report     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)


def log_handler(phase: str, message: str):
    """Pretty-print log messages with colors."""
    color = PHASE_COLORS.get(phase, Colors.WHITE)
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = f"{Colors.DIM}[{timestamp}]{Colors.RESET}"
    phase_tag = f"{color}[{phase.upper():>10}]{Colors.RESET}"
    print(f"  {prefix} {phase_tag} {message}")


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Research & Solution Architect Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py "Design a CCaaS migration plan from Avaya to Genesys Cloud"
  python run.py "Compare CTI integration approaches for Cisco UCCE vs Amazon Connect"
  python run.py --provider openai --model gpt-4o "Analyze SIP trunk failover architectures"
  python run.py --depth exhaustive "PBX to UCaaS migration best practices"
        """
    )
    parser.add_argument("goal", nargs="?", help="Research goal or question")
    parser.add_argument("--provider", "-p", help="LLM provider (ollama/openai/anthropic/google)")
    parser.add_argument("--model", "-m", help="Model name to use")
    parser.add_argument("--depth", "-d", choices=["quick", "detailed", "exhaustive"],
                        help="Research depth (default: from config)")
    parser.add_argument("--config", "-c", default="config.yaml", help="Config file path")
    parser.add_argument("--output", "-o", help="Output filename for the report")

    args = parser.parse_args()

    print_banner()

    # Load config
    config = Config(args.config)

    # Override config with CLI args
    if args.provider:
        config._config["provider"] = args.provider
    if args.model:
        provider_name = config.provider_name
        if provider_name in config._config:
            config._config[provider_name]["model"] = args.model
        else:
            config._config[provider_name] = {"model": args.model}
    if args.depth:
        if "agent" not in config._config:
            config._config["agent"] = {}
        config._config["agent"]["research_depth"] = args.depth

    # Get goal
    if args.goal:
        goal = args.goal
    else:
        print(f"  {Colors.CYAN}{Colors.BOLD}Enter your research goal:{Colors.RESET}")
        print(f"  {Colors.DIM}(e.g., 'Design a CCaaS migration from Avaya to Genesys Cloud'){Colors.RESET}")
        print()
        goal = input(f"  {Colors.YELLOW}▶ {Colors.RESET}").strip()
        if not goal:
            print(f"  {Colors.RED}No goal provided. Exiting.{Colors.RESET}")
            sys.exit(1)

    print()
    print(f"  {Colors.BOLD}{'═' * 60}{Colors.RESET}")
    print(f"  {Colors.BOLD}{Colors.CYAN}  AGENT STARTING AUTONOMOUS RESEARCH{Colors.RESET}")
    print(f"  {Colors.BOLD}{'═' * 60}{Colors.RESET}")
    print()

    # Create and run agent
    agent = AutonomousAgent(config)
    agent.set_log_callback(log_handler)

    try:
        report = agent.run(goal)

        # Save report
        filepath = agent.save_report(report, filename=args.output)

        print()
        print(f"  {Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print(f"  {Colors.BOLD}{Colors.GREEN}  ✅ RESEARCH COMPLETE{Colors.RESET}")
        print(f"  {Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print()
        print(f"  {Colors.GREEN}📄 Report saved to: {Colors.BOLD}{filepath}{Colors.RESET}")
        print(f"  {Colors.GREEN}📊 Findings: {len(agent.memory.findings)}{Colors.RESET}")
        print(f"  {Colors.GREEN}🔄 Iterations: {agent.memory.iteration}{Colors.RESET}")
        print()

        # Also print the report to console
        print(f"  {Colors.DIM}{'─' * 60}{Colors.RESET}")
        print(f"\n{report}\n")

    except KeyboardInterrupt:
        print(f"\n  {Colors.YELLOW}⚠ Agent interrupted by user.{Colors.RESET}")
        sys.exit(0)
    except ConnectionError as e:
        print(f"\n  {Colors.RED}❌ Connection Error: {e}{Colors.RESET}")
        print(f"  {Colors.YELLOW}💡 Make sure your LLM provider is running.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n  {Colors.RED}❌ Error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
