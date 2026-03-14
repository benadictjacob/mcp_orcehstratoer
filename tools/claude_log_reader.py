import os
import sys

# Add the log directory path
log_dir = r"C:\Users\VICTUS\AppData\Roaming\Claude\logs"

def list_files():
    """List all files in the log directory"""
    try:
        if not os.path.exists(log_dir):
            return f"Directory not found: {log_dir}"
        
        files = os.listdir(log_dir)
        result = []
        for file in files:
            full_path = os.path.join(log_dir, file)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                from datetime import datetime
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                result.append(f"{file} - {size/1024:.2f} KB - Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(result) if result else "No files found"
    except Exception as e:
        return f"Error: {str(e)}"

def read_file(filename, lines=50):
    """Read last N lines from a file"""
    try:
        filepath = os.path.join(log_dir, filename)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            return ''.join(last_lines)
    except Exception as e:
        return f"Error reading {filename}: {str(e)}"

def run(input_str=""):
    """
    Commands:
    - list: List all log files
    - read:filename:lines: Read file (default 50 lines)
    """
    if not input_str.strip():
        return "Commands: 'list' or 'read:filename:lines'"
    
    parts = input_str.split(':')
    command = parts[0].strip().lower()
    
    if command == 'list':
        return list_files()
    elif command == 'read':
        if len(parts) < 2:
            return "Usage: read:filename:lines"
        filename = parts[1].strip()
        lines = int(parts[2]) if len(parts) > 2 else 50
        return read_file(filename, lines)
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(run("list"))
