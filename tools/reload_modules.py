import sys
import importlib

def run(input_str=""):
    """
    Reload all modules in the registry
    """
    try:
        modules_to_reload = [
            'calculator',
            'excel_handler', 
            'claude_log_reader',
            'log_analyzer'
        ]
        
        reloaded = []
        failed = []
        
        for module_name in modules_to_reload:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    reloaded.append(module_name)
                else:
                    # Try to import it first
                    __import__(module_name)
                    reloaded.append(f"{module_name} (newly imported)")
            except Exception as e:
                failed.append(f"{module_name}: {str(e)}")
        
        result = "=== Module Reload Results ===\n\n"
        if reloaded:
            result += "[SUCCESS] Reloaded modules:\n"
            for mod in reloaded:
                result += f"  - {mod}\n"
        
        if failed:
            result += "\n[FAILED] Could not reload:\n"
            for fail in failed:
                result += f"  - {fail}\n"
        
        return result
    except Exception as e:
        return f"Error during reload: {str(e)}"
