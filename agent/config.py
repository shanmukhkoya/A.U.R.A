"""Configuration management for the Autonomous Agent."""
import os
import yaml
from typing import Any, Optional
from dotenv import load_dotenv

# Models known to be small (< 7B params) — need optimized settings
SMALL_MODELS = {
    "phi3", "phi3:latest", "phi3:mini",
    "gemma2:2b", "gemma:2b", "gemma2:2b-instruct",
    "tinyllama", "tinyllama:latest",
    "qwen2:0.5b", "qwen2:1.5b",
    "stablelm2", "stablelm2:1.6b",
    "phi", "phi:latest",
}


class Config:
    """Loads and manages configuration from config.yaml and .env files."""

    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()  # Load .env file
        self._config = self._load_yaml(config_path)

    def _load_yaml(self, path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"⚠ Config file '{path}' not found. Using defaults.")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation (e.g., 'agent.max_iterations')."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def provider_name(self) -> str:
        return self.get("provider", "ollama")

    @property
    def provider_config(self) -> dict:
        """Get the config for the active provider, injecting API keys from env."""
        name = self.provider_name
        cfg = dict(self.get(name, {}))

        # Inject API keys from environment variables
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
        }
        if name in key_map:
            cfg["api_key"] = os.getenv(key_map[name], cfg.get("api_key"))

        return cfg

    @property
    def max_iterations(self) -> int:
        return self.get("agent.max_iterations", 3)

    @property
    def max_search_results(self) -> int:
        return self.get("agent.max_search_results", 5)

    @property
    def research_depth(self) -> str:
        return self.get("agent.research_depth", "detailed")

    @property
    def output_dir(self) -> str:
        return self.get("output.directory", "outputs")

    @property
    def small_model_mode(self) -> bool:
        """Auto-detect if we're using a small model that needs optimized settings."""
        # Explicit override in config
        explicit = self.get("agent.small_model_mode")
        if explicit is not None:
            return bool(explicit)
        # Auto-detect from model name
        provider = self.provider_name
        model = self.get(f"{provider}.model", "").lower()
        return any(model.startswith(s) for s in SMALL_MODELS)

    @property
    def max_content_chars(self) -> int:
        """Max chars of web content to send to LLM per query."""
        return 2000 if self.small_model_mode else 6000

    @property
    def max_pages_to_extract(self) -> int:
        """How many web pages to extract full content from."""
        return 2 if self.small_model_mode else 3

    @property
    def max_report_tokens(self) -> int:
        """Max tokens for the final report generation."""
        return 2000 if self.small_model_mode else 8000

    @property
    def max_analysis_tokens(self) -> int:
        """Max tokens for per-query analysis."""
        return 500 if self.small_model_mode else 4096
