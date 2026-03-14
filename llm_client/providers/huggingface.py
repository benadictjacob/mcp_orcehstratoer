import os
import requests
from typing import List, Dict, Any, Optional
from llm_client.base import BaseLLM
from llm_client.exceptions import LLMConnectionError, LLMAuthenticationError, LLMAPIError

class HuggingFaceProvider(BaseLLM):
    """
    Provider for Hugging Face Inference API.
    """
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2", base_url: str = "https://api-inference.huggingface.co/models/", api_key: str = None, **kwargs):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("HF_API_KEY")
        self.timeout = kwargs.get("timeout", 120)

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise LLMAuthenticationError("Hugging Face API key is missing.")
        return {"Authorization": f"Bearer {self.api_key}"}

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/{self.model}"
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250, "return_full_text": False}}
        
        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                return result[0]["generated_text"].strip()
            elif isinstance(result, dict) and "error" in result:
                raise LLMAPIError(f"Hugging Face API Error: {result['error']}")
            else:
                return str(result)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise LLMAuthenticationError("Invalid Hugging Face API key.")
            raise LLMAPIError(f"Hugging Face HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
             raise LLMConnectionError(f"Failed to connect to Hugging Face: {e}")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Simple chat implementation converting messages to a prompt string
        # Ideally, use a template, but for now simple concatenation
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        
        prompt += "Assistant: "
        return self.generate(prompt)

    def health_check(self) -> bool:
        try:
            # Simple check by generating a token
            self.generate("Hello")
            return True
        except Exception:
            return False
