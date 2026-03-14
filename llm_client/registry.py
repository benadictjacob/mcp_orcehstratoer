"""LLM Provider Registry - Dynamic provider registration and lookup."""

from typing import Dict, Type
from llm_client.base import BaseLLM
from llm_client.exceptions import LLMProviderNotFoundError


class LLMRegistry:
    """
    Registry for LLM providers.
    
    Maps provider names to provider classes for dynamic lookup.
    No provider logic inside registry - only registration and retrieval.
    
    Usage:
        # Register a provider
        LLMRegistry.register("my_provider", MyProviderClass)
        
        # Get a provider class
        provider_class = LLMRegistry.get("ollama")
        
        # List all providers
        providers = LLMRegistry.list_providers()
    """
    
    _providers: Dict[str, Type[BaseLLM]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[BaseLLM]) -> None:
        """
        Register a provider adapter.
        
        Args:
            name: Provider identifier (e.g., "ollama", "openai")
            provider_class: Class that inherits from BaseLLM
            
        Raises:
            TypeError: If provider_class doesn't inherit from BaseLLM
        """
        if not issubclass(provider_class, BaseLLM):
            raise TypeError(f"{provider_class.__name__} must inherit from BaseLLM")
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get(cls, name: str) -> Type[BaseLLM]:
        """
        Get a provider class by name.
        
        Args:
            name: Provider identifier
            
        Returns:
            Provider class
            
        Raises:
            LLMProviderNotFoundError: If provider not registered
        """
        name_lower = name.lower()
        if name_lower not in cls._providers:
            available = ", ".join(cls._providers.keys()) or "none"
            raise LLMProviderNotFoundError(
                f"Provider '{name}' not found. Available: {available}"
            )
        return cls._providers[name_lower]
    
    @classmethod
    def list_providers(cls) -> list:
        """
        List all registered provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            name: Provider identifier
            
        Returns:
            True if registered, False otherwise
        """
        return name.lower() in cls._providers
