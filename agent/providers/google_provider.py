"""Google Gemini LLM Provider."""
import requests
from typing import List, Dict, Optional
from .base import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
    """Provider for Google Gemini models."""

    API_BASE = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, model: str = "gemini-2.0-flash",
                 api_key: Optional[str] = None, **kwargs):
        super().__init__(model=model, api_key=api_key)

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                 max_tokens: int = 4096) -> str:
        if not self.api_key:
            raise ValueError("Google API key not set. Add GOOGLE_API_KEY to your .env file.")

        # Convert OpenAI-style messages to Gemini format
        contents = []
        system_instruction = None

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

        try:
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            }
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

            response = requests.post(
                f"{self.API_BASE}/models/{self.model}:generateContent?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Google API error: {e.response.status_code} — {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Google Gemini generation failed: {e}")

    def is_available(self) -> bool:
        return bool(self.api_key)
