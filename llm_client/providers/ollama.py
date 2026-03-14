"""Ollama Provider - Local LLM via HTTP."""

import requests
from typing import List, Dict

from llm_client.base import BaseLLM
from llm_client.exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMProviderError,
    LLMModelNotFoundError,
)


class OllamaProvider(BaseLLM):
    """
    Ollama provider for local LLM inference.
    
    Uses HTTP to communicate with Ollama server.
    Endpoint: POST /api/chat
    
    Usage:
        provider = OllamaProvider(model="llama3")
        response = provider.generate("Explain Python")
    """
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL = "llama3.2"
    
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        timeout: int = 60,
        **kwargs
    ):
        """
        Initialize Ollama provider.
        
        Args:
            model: Model name (default: llama3.2)
            base_url: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        super().__init__(
            model=model or self.DEFAULT_MODEL,
            base_url=base_url or self.DEFAULT_BASE_URL,
            **kwargs
        )
        self.timeout = timeout
    
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
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        
        # Add optional parameters
        if self.config.get("temperature") is not None:
            payload["options"] = payload.get("options", {})
            payload["options"]["temperature"] = self.config["temperature"]
        
        if self.config.get("system_prompt"):
            payload["system"] = self.config["system_prompt"]
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                raise LLMModelNotFoundError(
                    f"Model '{self.model}' not found",
                    provider="ollama"
                )
            
            if response.status_code != 200:
                raise LLMProviderError(
                    f"Ollama error: {response.text}",
                    status_code=response.status_code,
                    provider="ollama"
                )
            
            data = response.json()
            return data.get("message", {}).get("content", "")
            
        except requests.exceptions.ConnectionError:
            raise LLMConnectionError(
                "Cannot connect to Ollama. Is it running?",
                provider="ollama"
            )
        except requests.exceptions.Timeout:
            raise LLMTimeoutError(
                f"Request timed out after {self.timeout}s",
                provider="ollama"
            )
    
    def health_check(self) -> bool:
        """
        Check if Ollama is available.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> list:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except Exception:
            return []
