"""
llm_tool.py
===========

Runtime-compatible tool that bridges the llm_client library
into the dynamic capability system.

This tool is registered in registry.json and dispatched by runtime.py.
It reads llm_config.json to determine the active provider.

Commands:
    generate:<prompt>       → Generate text from a prompt
    chat:<json_messages>    → Multi-turn chat (JSON array of {role, content})
    health                  → Check if current provider is healthy
    providers               → List all registered LLM providers
    switch:<provider_name>  → Switch the active provider at runtime
    config                  → Show current configuration

IMPORTANT:
    This file lives in tools/ but imports from llm_client/ at project root.
    It does NOT contain LLM logic — only routing and config reading.
"""

import sys
import json
import os
from pathlib import Path

# Ensure project root is on sys.path so llm_client can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm_client import LLMClient

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

CONFIG_FILE = PROJECT_ROOT / "llm_config.json"


def _load_config() -> dict:
    """Load LLM configuration from llm_config.json."""
    if not CONFIG_FILE.exists():
        return {"default_provider": "mock", "providers": {"mock": {}}}
    return json.loads(CONFIG_FILE.read_text())


def _save_config(config: dict) -> None:
    """Persist config changes back to llm_config.json."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def _build_client(config: dict = None) -> LLMClient:
    """Build an LLMClient from the current config."""
    if config is None:
        config = _load_config()

    provider_name = config.get("default_provider", "mock")
    provider_cfg = config.get("providers", {}).get(provider_name, {})

    # Resolve API key from environment variable if specified
    api_key = None
    api_key_env = provider_cfg.get("api_key_env")
    if api_key_env:
        api_key = os.environ.get(api_key_env)

    return LLMClient(
        provider=provider_name,
        model=provider_cfg.get("model"),
        base_url=provider_cfg.get("base_url"),
        api_key=api_key,
        timeout=provider_cfg.get("timeout", 60),
    )


# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------------------------

def _cmd_generate(prompt: str) -> str:
    client = _build_client()
    return client.generate(prompt)


def _cmd_chat(json_messages: str) -> str:
    messages = json.loads(json_messages)
    client = _build_client()
    return client.chat(messages)


def _cmd_health() -> str:
    config = _load_config()
    provider_name = config.get("default_provider", "mock")
    client = _build_client(config)
    healthy = client.health_check()
    return f"{provider_name} provider is healthy: {healthy}"


def _cmd_providers() -> str:
    providers = LLMClient.list_providers()
    return "Registered providers: " + ", ".join(providers)


def _cmd_switch(provider_name: str) -> str:
    config = _load_config()
    available = list(config.get("providers", {}).keys())

    if provider_name not in available:
        return f"Provider '{provider_name}' not in config. Available: {', '.join(available)}"

    config["default_provider"] = provider_name
    _save_config(config)
    return f"Switched to provider: {provider_name}"


def _cmd_config() -> str:
    config = _load_config()
    return json.dumps(config, indent=2)


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT (called by runtime.py via registry.json)
# ---------------------------------------------------------------------------

def run(input_str: str = "") -> str:
    """
    Main entry point for the LLM tool.

    Format: command:argument
    Examples:
        run("generate:Explain recursion")
        run("health")
        run("switch:ollama")
    """
    input_str = input_str.strip()

    if not input_str:
        return (
            "LLM Tool - Multi-provider LLM client\n"
            "Commands: generate:<prompt>, chat:<json>, health, providers, switch:<name>, config"
        )

    # Parse command:argument
    if ":" in input_str:
        command, _, argument = input_str.partition(":")
        command = command.strip().lower()
        argument = argument.strip()
    else:
        command = input_str.strip().lower()
        argument = ""

    try:
        if command == "generate":
            if not argument:
                return "Usage: generate:<prompt>"
            return _cmd_generate(argument)

        elif command == "chat":
            if not argument:
                return 'Usage: chat:[{"role":"user","content":"Hello"}]'
            return _cmd_chat(argument)

        elif command == "health":
            return _cmd_health()

        elif command == "providers":
            return _cmd_providers()

        elif command == "switch":
            if not argument:
                return "Usage: switch:<provider_name>"
            return _cmd_switch(argument)

        elif command == "config":
            return _cmd_config()

        else:
            return f"Unknown command: {command}. Use: generate, chat, health, providers, switch, config"

    except Exception as e:
        return f"LLM Error [{type(e).__name__}]: {e}"
