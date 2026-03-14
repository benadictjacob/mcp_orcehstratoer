"""
C Drive Manager - Comprehensive analysis for unnecessary files on Windows C: drive
"""
import os
import json
from pathlib import Path

def get_size_mb(path):
    """Calculate size of file or directory in MB"""
    try:
        if os.path.isfile(path):
            return os.path.getsize(path) / (1024 * 1024)
        
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except:
                    pass
        return total / (1024 * 1024)
    except:
        return 0

def scan_browser_cache(user_dir):
    """Scan browser cache folders"""
    findings = []
    
    browser_paths = [
        (user_dir / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache", "Chrome Cache"),
        (user_dir / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Code Cache", "Chrome Code Cache"),
        (user_dir / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache", "Edge Cache"),
        (user_dir / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache", "Edge Code Cache"),
        (user_dir / "AppData" / "Local" / "Mozilla" / "Firefox" / "Profiles", "Firefox Cache"),
        (user_dir / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache", "IE/Edge INetCache"),
    ]
    
    for cache_path, label in browser_paths:
        if cache_path.exists():
            size = get_size_mb(str(cache_path))
            if size > 10:
                findings.append({
                    "type": "BROWSER_CACHE",
                    "priority": "LOW",
                    "path": str(cache_path),
                    "size_mb": round(size, 2),
                    "description": label,
                    "action": "Safe to delete - will be recreated"
                })
    
    return findings

def scan_app_cache(user_dir):
    """Scan application cache folders"""
    findings = []
    
    cache_paths = [
        (user_dir / "AppData" / "Local" / "Packages", "Windows Store Apps Cache"),
        (user_dir / "AppData" / "Local" / "Discord" / "Cache", "Discord Cache"),
        (user_dir / "AppData" / "Roaming" / "Discord" / "Cache", "Discord Roaming Cache"),
        (user_dir / "AppData" / "Local" / "Microsoft" / "Windows" / "WebCache", "Windows Web Cache"),
        (user_dir / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer", "Windows Explorer Cache"),
    ]
    
    for cache_path, label in cache_paths:
        if cache_path.exists():
            size = get_size_mb(str(cache_path))
            if size > 50:
                findings.append({
                    "type": "APP_CACHE",
                    "priority": "LOW",
                    "path": str(cache_path),
                    "size_mb": round(size, 2),
                    "description": label,
                    "action": "Can be cleared"
                })
    
    return findings

def scan_windows_logs():
    """Scan Windows log files"""
    findings = []
    
    log_paths = [
        (r"C:\Windows\Logs", "Windows Logs"),
        (r"C:\Windows\Temp", "Windows Temp"),
        (r"C:\Windows\Prefetch", "Windows Prefetch"),
    ]
    
    for log_path, label in log_paths:
        if os.path.exists(log_path):
            size = get_size_mb(log_path)
            if size > 10:
                findings.append({
                    "type": "WINDOWS_LOGS",
                    "priority": "LOW",
                    "path": log_path,
                    "size_mb": round(size, 2),
                    "description": label,
                    "action": "Old logs can be deleted"
                })
    
    return findings

def run(input_str=""):
    """Main entry point for C drive analysis"""
    
    command = input_str.lower().strip()
    
    if not command or command == "help":
        return json.dumps({
            "commands": [
                "analyze - Full comprehensive analysis",
                "temp - Find temporary files",
                "cache - Find cache files",
                "recycle - Check Recycle Bin size",
                "downloads - Analyze Downloads folders",
                "old - Check for old Windows installations",
                "list - List all deletable files with details"
            ],
            "usage": "Use: run_capability with name='c_drive' and input='analyze'"
        }, indent=2)
    
    results = {
        "success": True,
        "command": command,
        "findings": []
    }
    
    if command in ["analyze", "list"]:
        # 1. Windows Temp
        if os.path.exists(r"C:\Windows\Temp"):
            size = get_size_mb(r"C:\Windows\Temp")
            if size > 10:
                results["findings"].append({
                    "type": "WINDOWS_TEMP",
                    "priority": "LOW",
                    "path": r"C:\Windows\Temp",
                    "size_mb": round(size, 2),
                    "description": "Windows system temp files",
                    "action": "Safe to delete"
                })
        
        # 2. System Temp
        if os.path.exists(r"C:\Temp"):
            size = get_size_mb(r"C:\Temp")
            if size > 10:
                results["findings"].append({
                    "type": "SYSTEM_TEMP",
                    "priority": "LOW",
                    "path": r"C:\Temp",
                    "size_mb": round(size, 2),
                    "description": "System temp folder",
                    "action": "Safe to delete"
                })
        
        # 3. User-specific analysis
        try:
            users_path = Path(r"C:\Users")
            if users_path.exists():
                for user_dir in users_path.iterdir():
                    if user_dir.is_dir() and user_dir.name not in ["Public", "Default", "All Users"]:
                        # User temp
                        temp_path = user_dir / "AppData" / "Local" / "Temp"
                        if temp_path.exists():
                            size = get_size_mb(str(temp_path))
                            if size > 10:
                                results["findings"].append({
                                    "type": "USER_TEMP",
                                    "priority": "LOW",
                                    "path": str(temp_path),
                                    "size_mb": round(size, 2),
                                    "description": f"User temp for {user_dir.name}",
                                    "action": "Safe to delete"
                                })
                        
                        # Browser caches
                        results["findings"].extend(scan_browser_cache(user_dir))
                        
                        # App caches
                        results["findings"].extend(scan_app_cache(user_dir))
                        
                        # Downloads
                        downloads_path = user_dir / "Downloads"
                        if downloads_path.exists():
                            size = get_size_mb(str(downloads_path))
                            if size > 100:
                                results["findings"].append({
                                    "type": "DOWNLOADS",
                                    "priority": "MEDIUM",
                                    "path": str(downloads_path),
                                    "size_mb": round(size, 2),
                                    "description": f"Downloads for {user_dir.name}",
                                    "action": "Review and delete old files"
                                })
        except Exception as e:
            results["scan_error"] = str(e)
        
        # 4. Recycle Bin
        recycle_bin = r"C:\$Recycle.Bin"
        if os.path.exists(recycle_bin):
            size = get_size_mb(recycle_bin)
            if size > 0:
                results["findings"].append({
                    "type": "RECYCLE_BIN",
                    "priority": "LOW",
                    "path": recycle_bin,
                    "size_mb": round(size, 2),
                    "description": "Items in Recycle Bin",
                    "action": "Empty Recycle Bin"
                })
        
        # 5. Windows.old
        windows_old = r"C:\Windows.old"
        if os.path.exists(windows_old):
            size = get_size_mb(windows_old)
            results["findings"].append({
                "type": "OLD_WINDOWS",
                "priority": "MEDIUM",
                "path": windows_old,
                "size_mb": round(size, 2),
                "description": "Previous Windows installation",
                "action": "Can delete if Windows works fine"
            })
        
        # 6. Windows Update cache
        update_cache = r"C:\Windows\SoftwareDistribution\Download"
        if os.path.exists(update_cache):
            size = get_size_mb(update_cache)
            if size > 100:
                results["findings"].append({
                    "type": "UPDATE_CACHE",
                    "priority": "LOW",
                    "path": update_cache,
                    "size_mb": round(size, 2),
                    "description": "Windows Update download cache",
                    "action": "Can be cleared"
                })
        
        # 7. Windows logs
        results["findings"].extend(scan_windows_logs())
        
        # 8. Package Cache
        package_cache = r"C:\ProgramData\Package Cache"
        if os.path.exists(package_cache):
            size = get_size_mb(package_cache)
            if size > 100:
                results["findings"].append({
                    "type": "PACKAGE_CACHE",
                    "priority": "MEDIUM",
                    "path": package_cache,
                    "size_mb": round(size, 2),
                    "description": "Software installation cache",
                    "action": "Review - may need for repairs"
                })
        
        # Calculate totals
        total_space = sum(f["size_mb"] for f in results["findings"])
        results["total_potential_space_mb"] = round(total_space, 2)
        results["total_potential_space_gb"] = round(total_space / 1024, 2)
        results["total_items_found"] = len(results["findings"])
        
        # Sort by size (largest first)
        results["findings"].sort(key=lambda x: x["size_mb"], reverse=True)
        
    elif command == "temp":
        temp_dirs = [r"C:\Windows\Temp", r"C:\Temp"]
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                size = get_size_mb(temp_dir)
                results["findings"].append({
                    "path": temp_dir,
                    "size_mb": round(size, 2)
                })
    
    elif command == "recycle":
        recycle_bin = r"C:\$Recycle.Bin"
        if os.path.exists(recycle_bin):
            size = get_size_mb(recycle_bin)
            results["findings"].append({
                "path": recycle_bin,
                "size_mb": round(size, 2)
            })
    
    elif command == "downloads":
        try:
            users_path = Path(r"C:\Users")
            if users_path.exists():
                for user_dir in users_path.iterdir():
                    if user_dir.is_dir():
                        downloads_path = user_dir / "Downloads"
                        if downloads_path.exists():
                            size = get_size_mb(str(downloads_path))
                            results["findings"].append({
                                "user": user_dir.name,
                                "path": str(downloads_path),
                                "size_mb": round(size, 2)
                            })
        except Exception as e:
            results["error"] = str(e)
    
    elif command == "old":
        windows_old = r"C:\Windows.old"
        if os.path.exists(windows_old):
            size = get_size_mb(windows_old)
            results["findings"].append({
                "path": windows_old,
                "size_mb": round(size, 2),
                "description": "Previous Windows installation"
            })
        else:
            results["message"] = "No Windows.old folder found"
    
    else:
        results["success"] = False
        results["error"] = f"Unknown command: {command}. Use 'help' to see available commands."
    
    return json.dumps(results, indent=2)
