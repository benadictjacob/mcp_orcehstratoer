"""
Comprehensive C Drive Analyzer - Find duplicates, large files, and space-saving opportunities
"""
import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict

def get_file_hash(filepath, chunk_size=8192):
    """Calculate MD5 hash of a file"""
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None

def scan_for_duplicates(paths_to_scan, min_size_mb=1):
    """Scan directories for duplicate files"""
    file_sizes = defaultdict(list)
    
    min_size_bytes = min_size_mb * 1024 * 1024
    
    for scan_path in paths_to_scan:
        if not os.path.exists(scan_path):
            continue
        
        try:
            for root, dirs, files in os.walk(scan_path):
                dirs[:] = [d for d in dirs if d not in ['System Volume Information', '$RECYCLE.BIN', 
                                                         'Windows', 'Program Files', 'Program Files (x86)',
                                                         'ProgramData', 'AppData']]
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        
                        if size >= min_size_bytes:
                            file_sizes[size].append(filepath)
                    except:
                        continue
        except:
            continue
    
    duplicates = []
    for size, files in file_sizes.items():
        if len(files) > 1:
            hash_map = defaultdict(list)
            for filepath in files:
                file_hash = get_file_hash(filepath)
                if file_hash:
                    hash_map[file_hash].append(filepath)
            
            for file_hash, duplicate_files in hash_map.items():
                if len(duplicate_files) > 1:
                    size_mb = size / (1024 * 1024)
                    duplicates.append({
                        "hash": file_hash,
                        "size_mb": round(size_mb, 2),
                        "count": len(duplicate_files),
                        "wasted_space_mb": round(size_mb * (len(duplicate_files) - 1), 2),
                        "files": duplicate_files
                    })
    
    return duplicates

def scan_large_files(paths_to_scan, min_size_mb=100):
    """Find large files"""
    large_files = []
    min_size_bytes = min_size_mb * 1024 * 1024
    
    for scan_path in paths_to_scan:
        if not os.path.exists(scan_path):
            continue
        
        try:
            for root, dirs, files in os.walk(scan_path):
                dirs[:] = [d for d in dirs if d not in ['Windows', '$RECYCLE.BIN', 
                                                         'System Volume Information']]
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        if size >= min_size_bytes:
                            size_mb = size / (1024 * 1024)
                            large_files.append({
                                "path": filepath,
                                "size_mb": round(size_mb, 2),
                                "extension": os.path.splitext(filename)[1].lower()
                            })
                    except:
                        continue
        except:
            continue
    
    large_files.sort(key=lambda x: x["size_mb"], reverse=True)
    return large_files

def analyze_by_extension(paths_to_scan):
    """Analyze disk usage by file extension"""
    extension_stats = defaultdict(lambda: {"count": 0, "total_size": 0})
    
    for scan_path in paths_to_scan:
        if not os.path.exists(scan_path):
            continue
        
        try:
            for root, dirs, files in os.walk(scan_path):
                dirs[:] = [d for d in dirs if d not in ['Windows', '$RECYCLE.BIN']]
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        ext = os.path.splitext(filename)[1].lower() or "no_extension"
                        extension_stats[ext]["count"] += 1
                        extension_stats[ext]["total_size"] += size
                    except:
                        continue
        except:
            continue
    
    result = []
    for ext, stats in extension_stats.items():
        result.append({
            "extension": ext,
            "count": stats["count"],
            "total_size_mb": round(stats["total_size"] / (1024 * 1024), 2),
            "total_size_gb": round(stats["total_size"] / (1024 * 1024 * 1024), 2)
        })
    
    result.sort(key=lambda x: x["total_size_mb"], reverse=True)
    return result

def run(input_str=""):
    """Main entry point"""
    
    command = input_str.lower().strip()
    
    if not command or command == "help":
        return json.dumps({
            "commands": [
                "duplicates - Find duplicate files (>1MB)",
                "large - Find large files (>100MB)",
                "extensions - Analyze disk usage by file type",
                "plan - Create complete space-saving plan"
            ]
        }, indent=2)
    
    user_paths = [
        r"C:\Users\VICTUS\Documents",
        r"C:\Users\VICTUS\Downloads",
        r"C:\Users\VICTUS\Desktop",
        r"C:\Users\VICTUS\Pictures",
        r"C:\Users\VICTUS\Videos",
        r"C:\Users\VICTUS\Music"
    ]
    
    results = {"success": True, "command": command}
    
    if command == "duplicates":
        results["duplicates"] = scan_for_duplicates(user_paths, min_size_mb=1)
        
        if results["duplicates"]:
            total_wasted = sum(d["wasted_space_mb"] for d in results["duplicates"])
            results["summary"] = {
                "duplicate_groups": len(results["duplicates"]),
                "total_wasted_space_mb": round(total_wasted, 2),
                "total_wasted_space_gb": round(total_wasted / 1024, 2)
            }
            results["duplicates"] = sorted(results["duplicates"], 
                                          key=lambda x: x["wasted_space_mb"], 
                                          reverse=True)[:50]
    
    elif command == "large":
        results["large_files"] = scan_large_files(user_paths, min_size_mb=100)[:50]
        
        if results["large_files"]:
            total_size = sum(f["size_mb"] for f in results["large_files"])
            results["summary"] = {
                "files_found": len(results["large_files"]),
                "total_size_gb": round(total_size / 1024, 2)
            }
    
    elif command == "extensions":
        results["extensions"] = analyze_by_extension(user_paths)[:30]
    
    elif command == "plan":
        duplicates = scan_for_duplicates(user_paths, min_size_mb=1)
        duplicate_space = sum(d["wasted_space_mb"] for d in duplicates)
        
        large_files = scan_large_files(user_paths, min_size_mb=100)
        
        extensions = analyze_by_extension(user_paths)
        
        results["plan"] = {
            "duplicates": {
                "count": len(duplicates),
                "wasted_space_gb": round(duplicate_space / 1024, 2),
                "top_10": sorted(duplicates, key=lambda x: x["wasted_space_mb"], reverse=True)[:10]
            },
            "large_files": {
                "count": len(large_files),
                "top_20": large_files[:20]
            },
            "file_types": {
                "top_10": extensions[:10]
            }
        }
    
    else:
        results["success"] = False
        results["error"] = "Unknown command"
    
    return json.dumps(results, indent=2)
