"""LLM Client - Unified interface to multiple LLM providers."""

from typing import List, Dict, Optional

from llm_client.base import BaseLLM
from llm_client.registry import LLMRegistry
from llm_client.exceptions import LLMError, LLMProviderNotFoundError


class LLMClient:
    """
    Unified LLM client with dynamic provider selection.
    
    Provides a single interface to multiple LLM providers.
    No provider-specific logic in this class - all handled by adapters.
    
    Usage:
        # Basic usage
        client = LLMClient(provider="ollama", model="llama3")
        response = client.generate("Explain system design")
        print(response)
        
        # With OpenAI-compatible API
        client = LLMClient(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="sk-..."
        )
        response = client.generate("Hello, world!")
        
        # Switching providers (no code change needed)
        client = LLMClient(provider="mock")  # For testing
    """
    
    def __init__(
        self,
        provider: str,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 60,
        **kwargs
    ):
        """
        Initialize the LLM client.
        
        Args:
            provider: Provider name ("ollama", "openai", "mock")
            model: Model identifier
            base_url: Override API base URL
            api_key: API key (if required)
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific configuration
            
        Raises:
            LLMProviderNotFoundError: If provider is not registered
        """
        self.provider_name = provider.lower()
        
        # Get provider class from registry
        provider_class = LLMRegistry.get(self.provider_name)
        
        # Initialize the provider
        self._provider: BaseLLM = provider_class(
            model=model,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            **kwargs
        )
    
    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt.
        
        This is the main API - same across all providers.
        
        Args:
            prompt: The input prompt
            
        Returns:
            Generated text as string
            
        Raises:
            LLMError: If generation fails
        """
        return self._provider.generate(prompt)
    
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
        return self._provider.chat(messages)
    
    def health_check(self) -> bool:
        """
        Check if the provider is available.
        
        Returns:
            True if healthy, False otherwise
        """
        return self._provider.health_check()
    
    def switch_provider(
        self,
        provider: str,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        **kwargs
    ) -> None:
        """
        Switch to a different provider.
        
        Args:
            provider: New provider name
            model: Model identifier
            base_url: Override API base URL
            api_key: API key (if required)
            **kwargs: Additional configuration
            
        Raises:
            LLMProviderNotFoundError: If provider is not registered
        """
        self.provider_name = provider.lower()
        provider_class = LLMRegistry.get(self.provider_name)
        self._provider = provider_class(
            model=model,
            base_url=base_url,
            api_key=api_key,
            **kwargs
        )
    
    @staticmethod
    def list_providers() -> list:
        """
        List all available providers.
        
        Returns:
            List of provider names
        """
        return LLMRegistry.list_providers()
