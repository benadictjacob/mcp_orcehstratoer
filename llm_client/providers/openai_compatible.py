"""OpenAI-Compatible Provider - Works with any OpenAI-style API."""

import os
import requests
from typing import List, Dict

from llm_client.base import BaseLLM
from llm_client.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMProviderError,
)


class OpenAICompatibleProvider(BaseLLM):
    """
    OpenAI-compatible provider using HTTP requests.
    
    Works with:
    - OpenAI API
    - Azure OpenAI
    - LocalAI
    - LM Studio
    - Any OpenAI-compatible endpoint
    
    Usage:
        # OpenAI
        provider = OpenAICompatibleProvider(
            model="gpt-3.5-turbo",
            api_key="sk-..."
        )
        
        # Custom endpoint
        provider = OpenAICompatibleProvider(
            model="local-model",
            base_url="http://localhost:8080/v1",
            api_key="not-needed"
        )
    """
    
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    DEFAULT_MODEL = "gpt-3.5-turbo"
    
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 60,
        **kwargs
    ):
        """
        Initialize OpenAI-compatible provider.
        
        Args:
            model: Model name (default: gpt-3.5-turbo)
            base_url: API base URL (default: OpenAI)
            api_key: API key (defaults to OPENAI_API_KEY env var)
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        super().__init__(
            model=model or self.DEFAULT_MODEL,
            base_url=base_url or self.DEFAULT_BASE_URL,
            **kwargs
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.timeout = timeout
    
    def _get_headers(self) -> dict:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt
            
        Returns:
            Generated text as string
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response from chat messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Assistant's response as string
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        # Add optional parameters
        if self.config.get("temperature") is not None:
            payload["temperature"] = self.config["temperature"]
        if self.config.get("max_tokens"):
            payload["max_tokens"] = self.config["max_tokens"]
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise LLMAuthenticationError(
                    "Invalid API key",
                    provider="openai"
                )
            
            if response.status_code == 429:
                raise LLMRateLimitError(
                    "Rate limit exceeded",
                    provider="openai"
                )
            
            if response.status_code != 200:
                raise LLMProviderError(
                    f"API error: {response.text}",
                    status_code=response.status_code,
                    provider="openai"
                )
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.ConnectionError:
            raise LLMConnectionError(
                f"Cannot connect to {self.base_url}",
                provider="openai"
            )
        except requests.exceptions.Timeout:
            raise LLMTimeoutError(
                f"Request timed out after {self.timeout}s",
                provider="openai"
            )
    
    def health_check(self) -> bool:
        """
        Check if API is available.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/models"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=5
            )
            return response.status_code in [200, 401]  # 401 means API is up but key issue
        except Exception:
            return False
