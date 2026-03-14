"""
Math operations module for MCP demo server - EXTENDED WITH LOG READING
"""
import json
import os
from datetime import datetime

def add_two_numbers(a, b):
    """Add two numbers and return result"""
    try:
        num_a = float(a)
        num_b = float(b)
        result = num_a + num_b
        return {
            "success": True,
            "result": result,
            "operation": f"{num_a} + {num_b} = {result}",
            "message": f"Successfully added {num_a} and {num_b} to get {result}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def read_logs(log_dir, command="list", params=""):
    """Read Claude Desktop logs dynamically"""
    try:
        if command == "list":
            if not os.path.exists(log_dir):
                return {"success": False, "error": f"Directory not found: {log_dir}"}
            
            files = []
            for file in os.listdir(log_dir):
                if os.path.isfile(os.path.join(log_dir, file)):
                    full_path = os.path.join(log_dir, file)
                    size = os.path.getsize(full_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    files.append({
                        "name": file,
                        "size_kb": round(size/1024, 2),
                        "modified": modified.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return {"success": True, "files": files, "count": len(files)}
        
        elif command == "read":
            parts = params.split(":", 1)
            filename = parts[0].strip()
            lines = int(parts[1]) if len(parts) > 1 else 100
            
            filepath = os.path.join(log_dir, filename)
            if not os.path.exists(filepath):
                return {"success": False, "error": f"File not found: {filepath}"}
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
            return {
                "success": True,
                "filename": filename,
                "lines_read": len(last_lines),
                "content": ''.join(last_lines)
            }
        
        elif command == "search":
            parts = params.split(":", 1)
            if len(parts) < 2:
                return {"success": False, "error": "Usage: search:filename:term"}
            
            filename = parts[0].strip()
            search_term = parts[1].strip()
            
            filepath = os.path.join(log_dir, filename)
            if not os.path.exists(filepath):
                return {"success": False, "error": f"File not found: {filepath}"}
            
            matches = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if search_term.lower() in line.lower():
                        matches.append(f"Line {line_num}: {line.strip()}")
                        if len(matches) >= 30:
                            break
            
            return {
                "success": True,
                "filename": filename,
                "search_term": search_term,
                "matches_found": len(matches),
                "matches": matches
            }
        
        else:
            return {"success": False, "error": f"Unknown command: {command}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def run(input_str=""):
    """Main entry point for the capability"""
    if not input_str:
        return json.dumps({"success": False, "error": "No input provided"})
    
    # Check if it's a log command (starts with "log:")
    if input_str.startswith("log:"):
        # Format: log:command:log_dir:params
        # Examples:
        #   log:list:C:\Users\VICTUS\AppData\Roaming\Claude\logs
        #   log:read:C:\Users\VICTUS\AppData\Roaming\Claude\logs:main.log:50
        #   log:search:C:\Users\VICTUS\AppData\Roaming\Claude\logs:main.log:error
        
        parts = input_str[4:].split(":", 2)  # Remove "log:" prefix
        if len(parts) < 2:
            return json.dumps({
                "success": False,
                "error": "Usage: log:command:log_dir:params",
                "commands": ["list", "read", "search"]
            })
        
        command = parts[0].strip()
        log_dir = parts[1].strip()
        params = parts[2] if len(parts) > 2 else ""
        
        result = read_logs(log_dir, command, params)
        return json.dumps(result, indent=2)
    
    # Otherwise, treat as calculator
    parts = input_str.strip().split()
    if len(parts) < 2:
        return json.dumps({"success": False, "error": "Please provide two numbers OR use log:command format"})
    
    result = add_two_numbers(parts[0], parts[1])
    return json.dumps(result)
