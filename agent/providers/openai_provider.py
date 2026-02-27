"""OpenAI-compatible LLM Provider — works with OpenAI, Groq, Together, etc."""
import requests
from typing import List, Dict, Optional
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """
    Provider for OpenAI API and any OpenAI-compatible endpoint.
    Works with: OpenAI, Groq, Together AI, Azure OpenAI, LM Studio, etc.
    """

    def __init__(self, model: str = "gpt-4o-mini",
                 base_url: str = "https://api.openai.com/v1",
                 api_key: Optional[str] = None, **kwargs):
        super().__init__(model=model, base_url=base_url, api_key=api_key)

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                 max_tokens: int = 4096) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key not set. Add OPENAI_API_KEY to your .env file.")

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"OpenAI API error: {e.response.status_code} — {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")

    def is_available(self) -> bool:
        return bool(self.api_key)
