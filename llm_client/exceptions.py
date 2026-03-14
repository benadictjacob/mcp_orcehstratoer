"""LLM Client Exceptions - Centralized error handling."""


class LLMError(Exception):
    """Base exception for all LLM client errors."""
    
    def __init__(self, message: str, provider: str = None):
        self.message = message
        self.provider = provider
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.provider:
            return f"[{self.provider}] {self.message}"
        return self.message


class LLMConnectionError(LLMError):
    """Raised when unable to connect to the LLM provider (network failure)."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when a request times out."""
    pass


class LLMAuthenticationError(LLMError):
    """Raised when authentication fails (invalid API key)."""
    pass


class LLMAPIError(LLMError):
    """Raised when the API returns a general error."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class LLMProviderError(LLMError):
    """Raised when the provider returns an error response."""
    
    def __init__(self, message: str, status_code: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class LLMProviderNotFoundError(LLMError):
    """Raised when requested provider is not registered."""
    pass


class LLMModelNotFoundError(LLMError):
    """Raised when requested model is not available."""
    pass
