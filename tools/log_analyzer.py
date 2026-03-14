import os
import json
from datetime import datetime
from collections import Counter
import re

class LogAnalyzer:
    def __init__(self, log_directory):
        self.log_directory = log_directory
        
    def list_log_files(self):
        """List all log files in the directory"""
        try:
            files = []
            for file in os.listdir(self.log_directory):
                if file.endswith('.log'):
                    full_path = os.path.join(self.log_directory, file)
                    size = os.path.getsize(full_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    files.append({
                        'name': file,
                        'size': f"{size / 1024:.2f} KB",
                        'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
                    })
            return files
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def read_log_file(self, filename, lines=100):
        """Read last N lines from a log file"""
        try:
            filepath = os.path.join(self.log_directory, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(last_lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def analyze_errors(self, filename):
        """Extract and count error messages"""
        try:
            filepath = os.path.join(self.log_directory, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Common error patterns
            errors = re.findall(r'ERROR[:\s]+(.+?)(?:\n|$)', content, re.IGNORECASE)
            warnings = re.findall(r'WARN(?:ING)?[:\s]+(.+?)(?:\n|$)', content, re.IGNORECASE)
            exceptions = re.findall(r'Exception[:\s]+(.+?)(?:\n|$)', content, re.IGNORECASE)
            
            error_counter = Counter(errors)
            warning_counter = Counter(warnings)
            exception_counter = Counter(exceptions)
            
            result = {
                'total_errors': len(errors),
                'total_warnings': len(warnings),
                'total_exceptions': len(exceptions),
                'top_errors': error_counter.most_common(5),
                'top_warnings': warning_counter.most_common(5),
                'top_exceptions': exception_counter.most_common(5)
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error analyzing errors: {str(e)}"
    
    def search_logs(self, search_term, filename=None):
        """Search for specific text in log files"""
        try:
            results = []
            files_to_search = [filename] if filename else [f for f in os.listdir(self.log_directory) if f.endswith('.log')]
            
            for file in files_to_search:
                filepath = os.path.join(self.log_directory, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if search_term.lower() in line.lower():
                                results.append({
                                    'file': file,
                                    'line_number': i,
                                    'content': line.strip()
                                })
                except:
                    continue
            
            if results:
                return json.dumps(results[:50], indent=2)  # Limit to 50 results
            else:
                return f"No results found for '{search_term}'"
        except Exception as e:
            return f"Error searching logs: {str(e)}"
    
    def get_statistics(self, filename):
        """Get general statistics about a log file"""
        try:
            filepath = os.path.join(self.log_directory, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            errors = sum(1 for line in lines if 'error' in line.lower())
            warnings = sum(1 for line in lines if 'warn' in line.lower())
            info = sum(1 for line in lines if 'info' in line.lower())
            debug = sum(1 for line in lines if 'debug' in line.lower())
            
            # Try to find timestamps
            timestamps = []
            for line in lines:
                # Common timestamp patterns
                match = re.search(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', line)
                if match:
                    timestamps.append(match.group())
            
            result = {
                'filename': filename,
                'total_lines': total_lines,
                'errors': errors,
                'warnings': warnings,
                'info': info,
                'debug': debug,
                'first_timestamp': timestamps[0] if timestamps else 'N/A',
                'last_timestamp': timestamps[-1] if timestamps else 'N/A'
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting statistics: {str(e)}"
    
    def get_recent_activity(self, minutes=30):
        """Get recent log entries from all files"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            recent_entries = []
            
            for file in os.listdir(self.log_directory):
                if not file.endswith('.log'):
                    continue
                    
                filepath = os.path.join(self.log_directory, file)
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if modified_time >= cutoff_time:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        recent_entries.append({
                            'file': file,
                            'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'last_10_lines': ''.join(lines[-10:])
                        })
            
            if recent_entries:
                return json.dumps(recent_entries, indent=2)
            else:
                return f"No log activity in the last {minutes} minutes"
        except Exception as e:
            return f"Error getting recent activity: {str(e)}"


def run(input_str=""):
    """
    Main function to handle log analysis requests
    Input format: 'command:log_directory:parameters'
    Commands: list, read, errors, search, stats, recent
    
    Examples:
    - 'list:C:/Users/YourName/AppData/Roaming/Claude/logs'
    - 'read:C:/Users/YourName/AppData/Roaming/Claude/logs:main.log:50'
    - 'errors:C:/Users/YourName/AppData/Roaming/Claude/logs:main.log'
    - 'search:C:/Users/YourName/AppData/Roaming/Claude/logs:error:main.log'
    - 'stats:C:/Users/YourName/AppData/Roaming/Claude/logs:main.log'
    - 'recent:C:/Users/YourName/AppData/Roaming/Claude/logs:30'
    """
    if not input_str.strip():
        return """Log Analyzer Commands:
- list:<log_directory> - List all log files
- read:<log_directory>:<filename>:<lines> - Read last N lines (default 100)
- errors:<log_directory>:<filename> - Analyze errors and warnings
- search:<log_directory>:<search_term>:<filename> - Search logs (filename optional)
- stats:<log_directory>:<filename> - Get file statistics
- recent:<log_directory>:<minutes> - Get recent activity (default 30 min)

Example: list:C:/Users/YourName/AppData/Roaming/Claude/logs"""
    
    try:
        parts = input_str.split(':', 1)
        if len(parts) < 2:
            return "Invalid format. Use: command:log_directory:parameters"
        
        command = parts[0].strip().lower()
        remaining = parts[1]
        
        # Parse log directory and additional parameters
        remaining_parts = remaining.split(':', 1)
        log_directory = remaining_parts[0].strip()
        
        if not os.path.exists(log_directory):
            return f"Log directory not found: {log_directory}"
        
        analyzer = LogAnalyzer(log_directory)
        
        if command == 'list':
            files = analyzer.list_log_files()
            return json.dumps(files, indent=2)
        
        elif command == 'read':
            if len(remaining_parts) < 2:
                return "Missing filename. Use: read:<log_directory>:<filename>:<lines>"
            params = remaining_parts[1].split(':')
            filename = params[0].strip()
            lines = int(params[1]) if len(params) > 1 else 100
            return analyzer.read_log_file(filename, lines)
        
        elif command == 'errors':
            if len(remaining_parts) < 2:
                return "Missing filename. Use: errors:<log_directory>:<filename>"
            filename = remaining_parts[1].strip()
            return analyzer.analyze_errors(filename)
        
        elif command == 'search':
            if len(remaining_parts) < 2:
                return "Missing search term. Use: search:<log_directory>:<search_term>:<filename>"
            params = remaining_parts[1].split(':', 1)
            search_term = params[0].strip()
            filename = params[1].strip() if len(params) > 1 else None
            return analyzer.search_logs(search_term, filename)
        
        elif command == 'stats':
            if len(remaining_parts) < 2:
                return "Missing filename. Use: stats:<log_directory>:<filename>"
            filename = remaining_parts[1].strip()
            return analyzer.get_statistics(filename)
        
        elif command == 'recent':
            minutes = 30
            if len(remaining_parts) > 1:
                try:
                    minutes = int(remaining_parts[1].strip())
                except:
                    pass
            return analyzer.get_recent_activity(minutes)
        
        else:
            return f"Unknown command: {command}"
    
    except Exception as e:
        return f"Error: {str(e)}"
