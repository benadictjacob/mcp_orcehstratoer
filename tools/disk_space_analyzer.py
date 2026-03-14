"""
Windows Disk Space Analyzer - Comprehensive C: Drive Analysis
Analyzes disk usage, finds duplicates, temporary files, and large space wasters
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

def format_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def get_directory_size(path):
    """Calculate total size of directory"""
    total = 0
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().size
                elif entry.is_dir(follow_symlinks=False):
                    total += get_directory_size(entry.path)
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass
    return total

def analyze_top_folders(base_path="C:\\"):
    """Analyze top-level folders by size"""
    folders = []
    try:
        for item in os.scandir(base_path):
            try:
                if item.is_dir(follow_symlinks=False):
                    name = item.name
                    # Skip system protected folders
                    if name in ['$Recycle.Bin', 'System Volume Information', 'Recovery']:
                        continue
                    
                    size = get_directory_size(item.path)
                    folders.append({
                        "name": name,
                        "path": item.path,
                        "size": size,
                        "size_human": format_size(size)
                    })
            except (PermissionError, OSError):
                continue
        
        folders.sort(key=lambda x: x["size"], reverse=True)
    except Exception as e:
        return {"error": str(e)}
    
    return folders[:20]  # Top 20

def find_large_files(base_path="C:\\", min_size_mb=100, max_results=50):
    """Find large files across C: drive"""
    large_files = []
    min_size = min_size_mb * 1024 * 1024
    
    skip_dirs = ['System Volume Information', '$Recycle.Bin', 'Windows\\WinSxS', 
                 'Windows\\System32', 'Windows\\SysWOW64', 'ProgramData\\Microsoft']
    
    def should_skip(path):
        for skip_dir in skip_dirs:
            if skip_dir in path:
                return True
        return False
    
    try:
        for root, dirs, files in os.walk(base_path):
            # Filter out system directories
            if should_skip(root):
                dirs.clear()
                continue
            
            dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
            
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    
                    if size >= min_size:
                        ext = os.path.splitext(file)[1].lower()
                        modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        large_files.append({
                            "name": file,
                            "path": file_path,
                            "size": size,
                            "size_human": format_size(size),
                            "extension": ext,
                            "modified": modified.strftime("%Y-%m-%d"),
                            "category": categorize_file(ext)
                        })
                        
                        if len(large_files) >= max_results * 2:
                            break
                except (PermissionError, OSError, FileNotFoundError):
                    continue
            
            if len(large_files) >= max_results * 2:
                break
                
    except Exception as e:
        return {"error": str(e)}
    
    large_files.sort(key=lambda x: x["size"], reverse=True)
    return large_files[:max_results]

def categorize_file(ext):
    """Categorize file by extension"""
    categories = {
        'installer': ['.exe', '.msi', '.dmg', '.pkg'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
        'document': ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'],
        'database': ['.db', '.sqlite', '.mdb'],
        'code': ['.py', '.js', '.java', '.cpp', '.cs']
    }
    
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return 'other'

def find_temp_files(base_path="C:\\"):
    """Find temporary and cache files"""
    temp_paths = [
        "Windows\\Temp",
        "Users\\*\\AppData\\Local\\Temp",
        "Users\\*\\AppData\\Local\\Microsoft\\Windows\\INetCache",
        "ProgramData\\Microsoft\\Windows\\WER"
    ]
    
    results = []
    total_size = 0
    
    try:
        for pattern in temp_paths:
            search = os.path.join(base_path, pattern)
            for path in Path(base_path).glob(pattern):
                if path.is_dir():
                    try:
                        size = get_directory_size(str(path))
                        total_size += size
                        results.append({
                            "path": str(path),
                            "size": size,
                            "size_human": format_size(size),
                            "type": "temp_directory"
                        })
                    except (PermissionError, OSError):
                        continue
    except Exception:
        pass
    
    return {
        "locations": results,
        "total_size": total_size,
        "total_size_human": format_size(total_size),
        "count": len(results)
    }

def analyze_by_extension(base_path="C:\\Users"):
    """Group files by extension"""
    extensions = defaultdict(lambda: {"count": 0, "size": 0, "samples": []})
    
    skip_dirs = ['AppData\\Local\\Microsoft', 'AppData\\Local\\Packages']
    
    def should_skip(path):
        for skip in skip_dirs:
            if skip in path:
                return True
        return False
    
    try:
        for root, dirs, files in os.walk(base_path):
            if should_skip(root):
                dirs.clear()
                continue
            
            for file in files:
                try:
                    ext = os.path.splitext(file)[1].lower() or 'no_extension'
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    
                    extensions[ext]["count"] += 1
                    extensions[ext]["size"] += size
                    
                    if len(extensions[ext]["samples"]) < 3:
                        extensions[ext]["samples"].append(file_path)
                        
                except (PermissionError, OSError):
                    continue
    except Exception:
        pass
    
    result = []
    for ext, data in extensions.items():
        result.append({
            "extension": ext,
            "count": data["count"],
            "total_size": data["size"],
            "total_size_human": format_size(data["size"]),
            "samples": data["samples"]
        })
    
    result.sort(key=lambda x: x["total_size"], reverse=True)
    return result[:30]

def find_duplicates(base_path, min_size_mb=1):
    """Find duplicate files by comparing file hashes"""
    hashes = defaultdict(list)
    min_size = min_size_mb * 1024 * 1024
    duplicates = []
    
    def file_hash(filepath, blocksize=65536):
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(blocksize)
                    if not data:
                        break
                    hasher.update(data)
            return hasher.hexdigest()
        except:
            return None
    
    try:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    
                    if size >= min_size:
                        file_h = file_hash(file_path)
                        if file_h:
                            hashes[file_h].append({
                                "path": file_path,
                                "size": size,
                                "name": file
                            })
                except (PermissionError, OSError):
                    continue
        
        # Find actual duplicates
        for hash_val, files in hashes.items():
            if len(files) > 1:
                total_waste = sum(f["size"] for f in files[1:])
                duplicates.append({
                    "files": [f["path"] for f in files],
                    "count": len(files),
                    "size_each": format_size(files[0]["size"]),
                    "total_waste": format_size(total_waste),
                    "waste_bytes": total_waste
                })
        
        duplicates.sort(key=lambda x: x["waste_bytes"], reverse=True)
        
    except Exception as e:
        return {"error": str(e)}
    
    return duplicates[:20]

def quick_analysis(base_path="C:\\"):
    """Quick overview of C: drive"""
    return {
        "top_folders": analyze_top_folders(base_path),
        "large_files": find_large_files(base_path, 100, 20),
        "temp_files": find_temp_files(base_path),
        "extensions": analyze_by_extension(os.path.join(base_path, "Users"))
    }

def run(input_data):
    """Main entry point"""
    parts = input_data.split(maxsplit=1)
    command = parts[0] if parts else "help"
    args = parts[1] if len(parts) > 1 else ""
    
    if command == "folders":
        path = args if args else "C:\\"
        return json.dumps(analyze_top_folders(path), indent=2)
    
    elif command == "large":
        parts = args.split()
        path = parts[0] if parts else "C:\\"
        min_size = int(parts[1]) if len(parts) > 1 else 100
        return json.dumps(find_large_files(path, min_size), indent=2)
    
    elif command == "temp":
        path = args if args else "C:\\"
        return json.dumps(find_temp_files(path), indent=2)
    
    elif command == "extensions":
        path = args if args else "C:\\Users"
        return json.dumps(analyze_by_extension(path), indent=2)
    
    elif command == "duplicates":
        path = args if args else "C:\\Users\\VICTUS\\Downloads"
        return json.dumps(find_duplicates(path), indent=2)
    
    elif command == "quick":
        path = args if args else "C:\\"
        return json.dumps(quick_analysis(path), indent=2)
    
    else:
        return """Windows Disk Space Analyzer Commands:

folders [path] - Analyze top folders by size (default C:\\)
large [path] [min_mb] - Find large files (default 100MB+)
temp [path] - Find temporary and cache files
extensions [path] - Analyze files by extension type
duplicates [path] - Find duplicate files (may be slow)
quick [path] - Quick overview of all analyses

Examples:
disk_analyzer folders C:\\
disk_analyzer large C:\\ 500
disk_analyzer temp
disk_analyzer extensions C:\\Users\\VICTUS
disk_analyzer duplicates C:\\Users\\VICTUS\\Downloads
disk_analyzer quick
"""
