import importlib.util
import sys
from pathlib import Path
from types import ModuleType

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR / "tools"


def _load_module(path: Path) -> ModuleType | None:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        print(f"[SPEC ERROR] {path.name}")
        return None

    if spec.name in sys.modules:
        del sys.modules[spec.name]

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"[LOAD ERROR] {path.name}: {e}")
        return None

    return module


def list_capabilities():
    caps = {}

    print("TOOLS_DIR:", TOOLS_DIR)
    print("FILES:", list(TOOLS_DIR.glob("*.py")))

    for file in TOOLS_DIR.glob("*.py"):
        if file.name.startswith("__"):
            continue

        module = _load_module(file)
        if module is None:
            continue

        functions = [
            name for name, obj in vars(module).items()
            if callable(obj) and not name.startswith("_")
        ]

        if functions:
            caps[file.stem] = functions

    return caps


def dispatch(action: str, context: str):
    if "." not in action:
        return "Invalid action format. Use tool.function"

    tool_name, func_name = action.split(".", 1)
    tool_file = TOOLS_DIR / f"{tool_name}.py"

    if not tool_file.exists():
        return f"Tool '{tool_name}' not found."

    module = _load_module(tool_file)
    if module is None:
        return f"Failed to load tool '{tool_name}'."

    if not hasattr(module, func_name):
        return f"Function '{func_name}' not found in tool '{tool_name}'."

    try:
        return getattr(module, func_name)(context)
    except Exception as e:
        return f"Error executing {action}: {e}"
