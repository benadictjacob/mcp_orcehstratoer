"""
Comprehensive C: Drive Space Analyzer MCP Tool
Analyzes entire C: drive for space usage
"""

import os
import json
from collections import defaultdict
from datetime import datetime

def format_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def get_directory_size(path):
    """Calculate total directory size"""
    total = 0
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += get_directory_size(entry.path)
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass
    return total

def analyze_top_folders(base="C:\\"):
    """Analyze all top-level folders in C: drive"""
    folders = []
    skip = ['$Recycle.Bin', 'System Volume Information', 'Recovery']
    
    try:
        for item in os.scandir(base):
            try:
                if item.is_dir(follow_symlinks=False) and item.name not in skip:
                    size = get_directory_size(item.path)
                    folders.append({
                        'name': item.name,
                        'path': item.path,
                        'size': size,
                        'size_human': format_size(size)
                    })
            except (PermissionError, OSError):
                continue
        
        folders.sort(key=lambda x: x['size'], reverse=True)
    except Exception as e:
        return {"error": str(e)}
    
    return folders

def find_large_files_in_folder(folder_path, min_mb=50, max_results=50):
    """Find large files in a specific folder"""
    min_size = min_mb * 1024 * 1024
    large_files = []
    
    try:
        for root, dirs, files in os.walk(folder_path):
            # Skip system folders
            dirs[:] = [d for d in dirs if d not in ['System Volume Information', '$Recycle.Bin']]
            
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    size = os.path.getsize(filepath)
                    
                    if size >= min_size:
                        ext = os.path.splitext(file)[1].lower()
                        
                        large_files.append({
                            'name': file,
                            'path': filepath,
                            'size': size,
                            'size_human': format_size(size),
                            'extension': ext
                        })
                        
                        if len(large_files) >= max_results * 2:
                            break
                            
                except (PermissionError, OSError, FileNotFoundError):
                    continue
            
            if len(large_files) >= max_results * 2:
                break
                
    except Exception as e:
        return {"error": str(e)}
    
    large_files.sort(key=lambda x: x['size'], reverse=True)
    return large_files[:max_results]

def analyze_user_folders(base="C:\\Users"):
    """Analyze user folders specifically"""
    user_analysis = {}
    
    try:
        for user in os.scandir(base):
            if user.is_dir():
                user_folders = {
                    'Downloads': 0,
                    'Documents': 0,
                    'Desktop': 0,
                    'Pictures': 0,
                    'Videos': 0,
                    'AppData': 0
                }
                
                for folder_name in user_folders.keys():
                    folder_path = os.path.join(user.path, folder_name)
                    if os.path.exists(folder_path):
                        user_folders[folder_name] = get_directory_size(folder_path)
                
                user_analysis[user.name] = {
                    'folders': {k: format_size(v) for k, v in user_folders.items()},
                    'total': format_size(sum(user_folders.values()))
                }
    except Exception as e:
        return {"error": str(e)}
    
    return user_analysis

def find_temp_files(base="C:\\"):
    """Find and calculate temporary files"""
    temp_locations = {
        'Windows Temp': os.path.join(base, 'Windows', 'Temp'),
        'Windows Update Cache': os.path.join(base, 'Windows', 'SoftwareDistribution', 'Download'),
    }
    
    results = {}
    total_size = 0
    
    for name, path in temp_locations.items():
        if os.path.exists(path):
            try:
                size = get_directory_size(path)
                results[name] = {
                    'path': path,
                    'size': size,
                    'size_human': format_size(size)
                }
                total_size += size
            except (PermissionError, OSError):
                results[name] = {'error': 'Access denied'}
    
    # Add user temp folders
    try:
        users_path = os.path.join(base, 'Users')
        for user in os.scandir(users_path):
            if user.is_dir():
                temp_path = os.path.join(user.path, 'AppData', 'Local', 'Temp')
                if os.path.exists(temp_path):
                    try:
                        size = get_directory_size(temp_path)
                        results[f'{user.name} Temp'] = {
                            'path': temp_path,
                            'size': size,
                            'size_human': format_size(size)
                        }
                        total_size += size
                    except (PermissionError, OSError):
                        pass
    except:
        pass
    
    return {
        'locations': results,
        'total_size': total_size,
        'total_size_human': format_size(total_size)
    }

def full_analysis(base="C:\\"):
    """Complete C: drive analysis"""
    return {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'top_folders': analyze_top_folders(base)[:15],
        'user_folders': analyze_user_folders(os.path.join(base, 'Users')),
        'temp_files': find_temp_files(base)
    }

def run(input_data):
    """Main entry point for MCP capability"""
    parts = input_data.split(maxsplit=1)
    command = parts[0] if parts else "help"
    args = parts[1] if len(parts) > 1 else ""
    
    if command == "folders":
        path = args if args else "C:\\"
        result = analyze_top_folders(path)
        return json.dumps(result, indent=2)
    
    elif command == "large":
        parts_args = args.split()
        path = parts_args[0] if parts_args else "C:\\Users\\VICTUS"
        min_size = int(parts_args[1]) if len(parts_args) > 1 else 50
        result = find_large_files_in_folder(path, min_size)
        return json.dumps(result, indent=2)
    
    elif command == "users":
        path = args if args else "C:\\Users"
        result = analyze_user_folders(path)
        return json.dumps(result, indent=2)
    
    elif command == "temp":
        path = args if args else "C:\\"
        result = find_temp_files(path)
        return json.dumps(result, indent=2)
    
    elif command == "full":
        path = args if args else "C:\\"
        result = full_analysis(path)
        return json.dumps(result, indent=2)
    
    else:
        return """C: Drive Analyzer Commands:

folders [path]        - Analyze top folders (default: C:\\)
large [path] [min_mb] - Find large files (default: C:\\Users\\VICTUS, 50MB)
users [path]          - Analyze user folders (default: C:\\Users)
temp [path]           - Find temporary files (default: C:\\)
full [path]           - Complete analysis (default: C:\\)

Examples:
c_analyzer folders
c_analyzer folders C:\\Program Files
c_analyzer large C:\\Users\\VICTUS\\Downloads 100
c_analyzer users
c_analyzer temp
c_analyzer full
"""
