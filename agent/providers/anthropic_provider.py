"""Anthropic Claude LLM Provider."""
import requests
from typing import List, Dict, Optional
from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Provider for Anthropic Claude models."""

    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def __init__(self, model: str = "claude-3-5-sonnet-20241022",
                 api_key: Optional[str] = None, **kwargs):
        super().__init__(model=model, api_key=api_key)

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                 max_tokens: int = 4096) -> str:
        if not self.api_key:
            raise ValueError("Anthropic API key not set. Add ANTHROPIC_API_KEY to your .env file.")

        # Anthropic requires system message to be separate
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)

        try:
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": chat_messages,
                "temperature": temperature,
            }
            if system_msg:
                payload["system"] = system_msg

            response = requests.post(
                self.API_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.API_VERSION,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Anthropic API error: {e.response.status_code} — {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Anthropic generation failed: {e}")

    def is_available(self) -> bool:
        return bool(self.api_key)
