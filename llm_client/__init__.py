"""
LLM Client Library - Multi-provider LLM connector.

A minimal, clean, production-style library for connecting to multiple
LLM providers through a unified interface.

Dependencies: Standard Library + requests only

Usage:
    from llm_client import LLMClient
    
    # Connect to Ollama
    client = LLMClient(provider="ollama", model="llama3")
    response = client.generate("Explain system design")
    print(response)
    
    # Switch to OpenAI (no code change needed!)
    client = LLMClient(provider="openai", model="gpt-3.5-turbo", api_key="sk-...")
    response = client.generate("Explain system design")
    print(response)
    
    # Use mock for testing
    client = LLMClient(provider="mock")
    response = client.generate("test")  # Returns mock response
"""

from llm_client.client import LLMClient
from llm_client.base import BaseLLM
from llm_client.registry import LLMRegistry
from llm_client.exceptions import (
    LLMError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMProviderError,
    LLMProviderNotFoundError,
    LLMProviderNotFoundError,
    LLMModelNotFoundError,
    LLMAPIError,
)

# Import providers for registration
from llm_client.providers import OllamaProvider, OpenAICompatibleProvider, MockProvider, HuggingFaceProvider

# Auto-register providers
LLMRegistry.register("ollama", OllamaProvider)
LLMRegistry.register("openai", OpenAICompatibleProvider)
LLMRegistry.register("mock", MockProvider)
LLMRegistry.register("huggingface", HuggingFaceProvider)


__version__ = "1.0.0"
__all__ = [
    # Main client
    "LLMClient",
    
    # Base class (for extending)
    "BaseLLM",
    
    # Registry
    "LLMRegistry",
    
    # Providers
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "MockProvider",
    
    # Exceptions
    "LLMError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMProviderError",
    "LLMProviderNotFoundError",
    "LLMModelNotFoundError",
    "LLMAPIError",
]
