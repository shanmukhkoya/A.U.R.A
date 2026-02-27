"""Abstract base class for all LLM providers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseLLMProvider(ABC):
    """
    Unified interface for all LLM providers.
    Every provider must implement the `generate` method.
    """

    def __init__(self, model: str, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                 max_tokens: int = 4096) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                      Roles: 'system', 'user', 'assistant'
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens in the response
            
        Returns:
            The generated text response as a string.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is currently available and configured."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model})"
