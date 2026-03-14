"""
server.py
==========

This file is the **static core** of the MCP server.

IMPORTANT DESIGN RULES:
- This file NEVER changes at runtime.
- No dynamic tool registration happens here.
- Claude NEVER edits this file.
- All dynamic behavior is routed through data (registry.json) and logic files.

MCP TOOLS DEFINED HERE:
1. self_edit        → privileged filesystem editor (core capability)
2. list_capabilities → reads dynamic registry
3. run_capability    → executes dynamic capabilities

Claude can call these tools DIRECTLY via MCP.
There is NO execute/action router involved.
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import json
import importlib
import sys

# ---------------------------------------------------------------------
# MCP SERVER INITIALIZATION
# ---------------------------------------------------------------------

server = FastMCP("static-runtime")

BASE_DIR = Path(__file__).parent.resolve()
TOOLS_DIR = BASE_DIR / "tools"
REGISTRY_FILE = TOOLS_DIR / "registry.json"


# ---------------------------------------------------------------------
# CORE TOOL 1: self_edit (PRIVILEGED)
# ---------------------------------------------------------------------
# This tool gives Claude the ability to:
# - create files
# - read files
# - write/update files
# - delete files
#
# SAFETY:
# - Claude is restricted to the tools/ directory
# - server.py cannot be modified
#
# NOTE:
# - This is NOT routed through any "action" system
# - This is a real MCP tool
# - Claude can call it directly
# ---------------------------------------------------------------------

def _safe_path(relative_path: str) -> Path:
    """
    Ensures Claude can only modify files inside tools/.
    Prevents directory traversal attacks.
    """
    path = (TOOLS_DIR / relative_path).resolve()
    if not str(path).startswith(str(TOOLS_DIR)):
        raise ValueError("Access outside tools/ is not allowed")
    return path


@server.tool()
def self_edit(
    edit_action: str,
    file_path: str,
    content: str = ""
) -> str:
    """
    Self-editing MCP tool.

    ACTIONS:
    - create : create a new file
    - read   : read an existing file
    - write  : overwrite an existing file
    - delete : delete a file

    This tool is the ONLY way Claude can modify the system.
    """
    path = _safe_path(file_path)

    if edit_action == "create":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Created {file_path}"

    if edit_action == "read":
        return path.read_text() if path.exists() else "File not found"

    if edit_action == "write":
        if not path.exists():
            return "File not found"
        path.write_text(content)
        return f"Updated {file_path}"

    if edit_action == "delete":
        if path.exists():
            path.unlink()
            return f"Deleted {file_path}"
        return "File not found"

    raise ValueError("Invalid action")


# ---------------------------------------------------------------------
# CORE TOOL 2: list_capabilities (DYNAMIC, DATA-DRIVEN)
# ---------------------------------------------------------------------
# Reads tools/registry.json and shows what dynamic capabilities exist.
#
# This is NOT how MCP advertises tools.
# This is only for Claude's planning and reasoning.
# ---------------------------------------------------------------------

@server.tool()
def list_capabilities() -> str:
    """
    Lists all dynamic capabilities defined in registry.json.
    """
    if not REGISTRY_FILE.exists():
        return "No capabilities registered."

    registry = json.loads(REGISTRY_FILE.read_text())

    return "\n".join(
        f"{name}: {cfg.get('description', '')}"
        for name, cfg in registry.items()
    )


# ---------------------------------------------------------------------
# CORE TOOL 3: run_capability (SINGLE EXECUTION GATE)
# ---------------------------------------------------------------------
# This is the ONLY way dynamic logic is executed.
#
# How it works:
# - Reads registry.json
# - Dynamically imports the module
# - Calls the configured function
#
# NO SERVER RESTART
# NO TOOL RE-REGISTRATION
# NO MCP RELOAD
# ---------------------------------------------------------------------

@server.tool()
def run_capability(name: str, capability_input: str = "") -> str:
    """
    Executes a dynamic capability defined in registry.json.
    """
    if not REGISTRY_FILE.exists():
        raise ValueError("registry.json not found")

    registry = json.loads(REGISTRY_FILE.read_text())

    if name not in registry:
        raise ValueError(f"Capability '{name}' not found")

    cfg = registry[name]
    module_path = cfg["module"]
    function_name = cfg["function"]

    # FIX: Add tools directory to Python path if not already there
    tools_dir = Path(__file__).parent / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

    # FIX: handle Python module caching
    if module_path in sys.modules:
        module = importlib.reload(sys.modules[module_path])
    else:
        module = importlib.import_module(module_path)

    fn = getattr(module, function_name)
    return fn(capability_input)

# ---------------------------------------------------------------------
# SERVER START
# ---------------------------------------------------------------------
# At this point:
# - MCP tools are registered
# - Claude sees self_edit, list_capabilities, run_capability
# - Dynamic behavior is fully data-driven
# ---------------------------------------------------------------------

if __name__ == "__main__":
    server.run()
