"""
Dynamic code executor - runs Python code without needing module imports
"""
import os
from datetime import datetime

def run(input_str=""):
    """
    Execute commands dynamically
    Format: command:params
    
    Commands:
    - list_logs:directory
    - read_log:directory:filename:lines
    - search_log:directory:filename:search_term
    """
    
    if not input_str.strip():
        return "Commands: list_logs, read_log, search_log"
    
    try:
        parts = input_str.split(':', 1)
        command = parts[0].strip().lower()
        params = parts[1] if len(parts) > 1 else ""
        
        if command == 'list_logs':
            log_dir = params.strip()
            if not log_dir:
                log_dir = r"C:\Users\VICTUS\AppData\Roaming\Claude\logs"
            
            if not os.path.exists(log_dir):
                return f"Directory not found: {log_dir}"
            
            files = []
            for file in os.listdir(log_dir):
                if os.path.isfile(os.path.join(log_dir, file)):
                    full_path = os.path.join(log_dir, file)
                    size = os.path.getsize(full_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    files.append(f"{file} | {size/1024:.2f} KB | {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return "\n".join(files) if files else "No files found"
        
        elif command == 'read_log':
            param_parts = params.split(':', 2)
            if len(param_parts) < 2:
                return "Usage: read_log:directory:filename:lines"
            
            log_dir = param_parts[0].strip()
            filename = param_parts[1].strip()
            lines = int(param_parts[2]) if len(param_parts) > 2 else 100
            
            filepath = os.path.join(log_dir, filename)
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(last_lines)
        
        elif command == 'search_log':
            param_parts = params.split(':', 2)
            if len(param_parts) < 3:
                return "Usage: search_log:directory:filename:search_term"
            
            log_dir = param_parts[0].strip()
            filename = param_parts[1].strip()
            search_term = param_parts[2].strip()
            
            filepath = os.path.join(log_dir, filename)
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"
            
            matches = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if search_term.lower() in line.lower():
                        matches.append(f"Line {line_num}: {line.strip()}")
                        if len(matches) >= 50:  # Limit results
                            break
            
            return "\n".join(matches) if matches else f"No matches found for '{search_term}'"
        
        else:
            return f"Unknown command: {command}"
            
    except Exception as e:
        return f"Error: {str(e)}"
