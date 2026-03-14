"""Mock Provider - For testing without real LLM calls."""

import random
from typing import List, Dict

from llm_client.base import BaseLLM


class MockProvider(BaseLLM):
    """
    Mock LLM provider for testing.
    
    Returns fake deterministic responses without making external calls.
    Useful for unit tests, CI/CD pipelines, and development.
    
    Usage:
        provider = MockProvider()
        response = provider.generate("test prompt")
        # Returns mock response without any API call
        
        # Or set a fixed response
        provider = MockProvider(fixed_response="Always this")
        response = provider.generate("anything")
        # Returns "Always this"
    """
    
    DEFAULT_RESPONSES = [
        "This is a mock response for testing purposes.",
        "Mock LLM is working correctly.",
        "Testing mode: No actual LLM call was made.",
    ]
    
    CODE_RESPONSES = [
        '''def hello_world():
    """Print hello world."""
    print("Hello, World!")
    return True''',
        '''def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b''',
        '''def factorial(n: int) -> int:
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)''',
    ]
    
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        fixed_response: str = None,
        **kwargs
    ):
        """
        Initialize mock provider.
        
        Args:
            model: Ignored (for API compatibility)
            base_url: Ignored (for API compatibility)
            fixed_response: If set, always return this response
            **kwargs: Additional configuration
        """
        super().__init__(model=model, base_url=base_url, **kwargs)
        self.fixed_response = fixed_response
        self._call_count = 0
    
    def generate(self, prompt: str) -> str:
        """
        Generate a mock response.
        
        Args:
            prompt: The input prompt (used to determine response type)
            
        Returns:
            Mock response string
        """
        self._call_count += 1
        
        # Return fixed response if set
        if self.fixed_response:
            return self.fixed_response
        
        # Detect code requests
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in ["code", "function", "def ", "class ", "program"]):
            return random.choice(self.CODE_RESPONSES)
        
        # Return random mock response
        return random.choice(self.DEFAULT_RESPONSES)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response from chat messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Mock response string
        """
        # Extract last user message
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break
        
        return self.generate(last_message)
    
    def health_check(self) -> bool:
        """
        Always returns True (mock is always available).
        
        Returns:
            True
        """
        return True
    
    def get_call_count(self) -> int:
        """Get the number of generate/chat calls made."""
        return self._call_count
    
    def reset(self) -> None:
        """Reset the mock state."""
        self._call_count = 0
