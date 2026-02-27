"""Ollama LLM Provider — for local models."""
import json
import requests
from typing import List, Dict, Optional
from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Provider for locally running Ollama models."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(model=model, base_url=base_url)

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                 max_tokens: int = 4096) -> str:
        try:
            # Use streaming to avoid massive timeouts on slow hardware.
            # Each chunk has its own timeout, so partial progress is never lost.
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                },
                timeout=(30, 300),  # (connect, read) — read applies per-chunk in streaming
                stream=True,
            )
            response.raise_for_status()

            # Accumulate streamed chunks
            full_response = []
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        full_response.append(content)
                    # Stop if the model signals done
                    if chunk.get("done", False):
                        break

            return "".join(full_response)
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: `ollama serve`"
            )
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        """List all available models in Ollama."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []
