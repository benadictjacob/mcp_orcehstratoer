"""Base class for all LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.
    
    All providers MUST inherit from this class and implement:
    - generate(prompt: str) -> str
    - chat(messages: list[dict]) -> str
    - health_check() -> bool
    
    Example:
        class MyProvider(BaseLLM):
            def generate(self, prompt: str) -> str:
                # Call your LLM API
                return response_text
    """
    
    def __init__(self, model: str = None, base_url: str = None, **kwargs):
        """
        Initialize the provider.
        
        Args:
            model: Model identifier (e.g., "llama3", "gpt-3.5-turbo")
            base_url: API base URL (if configurable)
            **kwargs: Additional provider-specific configuration
        """
        self.model = model
        self.base_url = base_url
        self.config = kwargs
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt
            
        Returns:
            Generated text as string
            
        Raises:
            LLMError: If generation fails
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response from chat messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                      e.g., [{"role": "user", "content": "Hello"}]
            
        Returns:
            Assistant's response as string
            
        Raises:
            LLMError: If generation fails
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the provider is available and responding.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
