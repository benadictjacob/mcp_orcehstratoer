"""Simple log analyzer wrapper for current directory"""
import os
import json
from log_analyzer import LogAnalyzer

def run(input_str=""):
    """
    Analyze log files in current directory
    Commands: list, read, errors, search, stats
    
    Examples:
    - 'list' - List all log files in current directory
    - 'read:test_application.log:20' - Read last 20 lines
    - 'errors:test_application.log' - Analyze errors
    - 'search:memory' - Search for 'memory' in all logs
    - 'stats:server.log' - Get statistics
    """
    try:
        # Use current directory
        log_directory = os.getcwd()
        analyzer = LogAnalyzer(log_directory)
        
        if not input_str.strip():
            return """Log Analyzer Commands (analyzes current directory):
- list - List all log files
- read:<filename>:<lines> - Read last N lines (default 100)
- errors:<filename> - Analyze errors and warnings
- search:<search_term> - Search in all logs
- stats:<filename> - Get file statistics

Examples:
- list
- read:test_application.log:20
- errors:server.log
- search:error
- stats:test_application.log"""
        
        parts = input_str.split(':', 1)
        command = parts[0].strip().lower()
        
        if command == 'list':
            files = analyzer.list_log_files()
            return json.dumps(files, indent=2)
        
        elif command == 'read':
            if len(parts) < 2:
                return "Missing filename. Use: read:<filename>:<lines>"
            params = parts[1].split(':')
            filename = params[0].strip()
            lines = int(params[1]) if len(params) > 1 else 100
            return analyzer.read_log_file(filename, lines)
        
        elif command == 'errors':
            if len(parts) < 2:
                return "Missing filename. Use: errors:<filename>"
            filename = parts[1].strip()
            return analyzer.analyze_errors(filename)
        
        elif command == 'search':
            if len(parts) < 2:
                return "Missing search term. Use: search:<search_term>"
            search_term = parts[1].strip()
            return analyzer.search_logs(search_term, None)
        
        elif command == 'stats':
            if len(parts) < 2:
                return "Missing filename. Use: stats:<filename>"
            filename = parts[1].strip()
            return analyzer.get_statistics(filename)
        
        else:
            return f"Unknown command: {command}"
    
    except Exception as e:
        return f"Error: {str(e)}"
