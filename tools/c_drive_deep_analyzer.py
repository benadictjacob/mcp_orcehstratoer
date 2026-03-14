"""
Deep C Drive Analyzer - Comprehensive system analysis
Analyzes: AppData, Windows, Program Files, System files, Hidden files, etc.
"""
import os
import json
from pathlib import Path
from collections import defaultdict
import subprocess

def get_folder_size(path):
    """Calculate folder size in MB"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except:
                    pass
    except:
        pass
    return total / (1024 * 1024)

def analyze_appdata():
    """Deep analysis of AppData folders"""
    results = []
    
    appdata_local = Path(r"C:\Users\VICTUS\AppData\Local")
    appdata_roaming = Path(r"C:\Users\VICTUS\AppData\Roaming")
    
    for base_path, label in [(appdata_local, "AppData Local"), (appdata_roaming, "AppData Roaming")]:
        if not base_path.exists():
            continue
        
        try:
            for item in base_path.iterdir():
                if item.is_dir():
                    size = get_folder_size(str(item))
                    if size > 50:  # Only report folders > 50MB
                        results.append({
                            "location": label,
                            "folder": item.name,
                            "path": str(item),
                            "size_mb": round(size, 2),
                            "size_gb": round(size / 1024, 2),
                            "type": "AppData Folder"
                        })
        except:
            pass
    
    results.sort(key=lambda x: x["size_mb"], reverse=True)
    return results

def analyze_program_files():
    """Analyze Program Files"""
    results = []
    
    program_paths = [
        Path(r"C:\Program Files"),
        Path(r"C:\Program Files (x86)")
    ]
    
    for base_path in program_paths:
        if not base_path.exists():
            continue
        
        try:
            for item in base_path.iterdir():
                if item.is_dir():
                    size = get_folder_size(str(item))
                    if size > 100:  # Only report > 100MB
                        results.append({
                            "program": item.name,
                            "path": str(item),
                            "size_mb": round(size, 2),
                            "size_gb": round(size / 1024, 2),
                            "type": "Installed Program"
                        })
        except:
            pass
    
    results.sort(key=lambda x: x["size_mb"], reverse=True)
    return results

def analyze_windows_folder():
    """Analyze Windows system folders"""
    results = []
    
    windows_path = Path(r"C:\Windows")
    important_folders = [
        "Logs", "Temp", "SoftwareDistribution", "Prefetch", 
        "Downloaded Program Files", "assembly", "Installer"
    ]
    
    if windows_path.exists():
        try:
            for folder in important_folders:
                folder_path = windows_path / folder
                if folder_path.exists():
                    size = get_folder_size(str(folder_path))
                    if size > 10:
                        results.append({
                            "folder": folder,
                            "path": str(folder_path),
                            "size_mb": round(size, 2),
                            "size_gb": round(size / 1024, 2),
                            "type": "Windows System Folder",
                            "safe_to_clean": folder in ["Logs", "Temp", "Prefetch"]
                        })
        except:
            pass
    
    results.sort(key=lambda x: x["size_mb"], reverse=True)
    return results

def analyze_programdata():
    """Analyze ProgramData folder"""
    results = []
    
    programdata_path = Path(r"C:\ProgramData")
    
    if programdata_path.exists():
        try:
            for item in programdata_path.iterdir():
                if item.is_dir():
                    size = get_folder_size(str(item))
                    if size > 50:
                        results.append({
                            "folder": item.name,
                            "path": str(item),
                            "size_mb": round(size, 2),
                            "size_gb": round(size / 1024, 2),
                            "type": "ProgramData Folder"
                        })
        except:
            pass
    
    results.sort(key=lambda x: x["size_mb"], reverse=True)
    return results

def check_system_files():
    """Check for large system files"""
    results = []
    
    system_files = [
        (r"C:\hiberfil.sys", "Hibernation File", "Can disable hibernation to free space"),
        (r"C:\pagefile.sys", "Page File", "Virtual memory - size can be adjusted"),
        (r"C:\swapfile.sys", "Swap File", "Windows swap file")
    ]
    
    for filepath, name, description in system_files:
        if os.path.exists(filepath):
            try:
                size = os.path.getsize(filepath) / (1024 * 1024)
                results.append({
                    "file": name,
                    "path": filepath,
                    "size_mb": round(size, 2),
                    "size_gb": round(size / 1024, 2),
                    "description": description,
                    "type": "System File"
                })
            except:
                pass
    
    return results

def get_disk_usage():
    """Get overall disk usage"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-PSDrive C | Select-Object Used,Free | ConvertTo-Json'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            used_gb = data['Used'] / (1024**3)
            free_gb = data['Free'] / (1024**3)
            total_gb = used_gb + free_gb
            
            return {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "used_percent": round((used_gb / total_gb) * 100, 2)
            }
    except:
        pass
    
    return None

def analyze_winsxs():
    """Analyze WinSxS folder (Windows component store)"""
    winsxs_path = r"C:\Windows\WinSxS"
    
    if os.path.exists(winsxs_path):
        size = get_folder_size(winsxs_path)
        return {
            "folder": "WinSxS",
            "path": winsxs_path,
            "size_mb": round(size, 2),
            "size_gb": round(size / 1024, 2),
            "description": "Windows component store - Can be cleaned with DISM",
            "type": "Windows Component Store"
        }
    return None

def run(input_str=""):
    """Main entry point"""
    
    command = input_str.lower().strip()
    
    if not command or command == "help":
        return json.dumps({
            "commands": [
                "full - Complete deep analysis of C: drive",
                "appdata - Analyze AppData folders",
                "programs - Analyze installed programs",
                "windows - Analyze Windows system folders",
                "system - Check system files (hiberfil, pagefile)",
                "disk - Show disk usage summary"
            ],
            "note": "Deep scan - will analyze entire C: drive"
        }, indent=2)
    
    results = {
        "success": True,
        "command": command
    }
    
    if command == "disk":
        results["disk_usage"] = get_disk_usage()
    
    elif command == "appdata":
        results["appdata_analysis"] = analyze_appdata()[:20]
        total = sum(item["size_mb"] for item in results["appdata_analysis"])
        results["summary"] = {
            "folders_analyzed": len(results["appdata_analysis"]),
            "total_size_gb": round(total / 1024, 2)
        }
    
    elif command == "programs":
        results["programs"] = analyze_program_files()[:30]
        total = sum(item["size_mb"] for item in results["programs"])
        results["summary"] = {
            "programs_found": len(results["programs"]),
            "total_size_gb": round(total / 1024, 2)
        }
    
    elif command == "windows":
        results["windows_folders"] = analyze_windows_folder()
        winsxs = analyze_winsxs()
        if winsxs:
            results["winsxs"] = winsxs
    
    elif command == "system":
        results["system_files"] = check_system_files()
        total = sum(item["size_mb"] for item in results["system_files"])
        results["summary"] = {
            "total_system_files_gb": round(total / 1024, 2)
        }
    
    elif command == "full":
        results["disk_usage"] = get_disk_usage()
        results["system_files"] = check_system_files()
        
        appdata = analyze_appdata()
        results["appdata_top_20"] = appdata[:20]
        results["appdata_total_gb"] = round(sum(x["size_mb"] for x in appdata) / 1024, 2)
        
        programs = analyze_program_files()
        results["programs_top_20"] = programs[:20]
        results["programs_total_gb"] = round(sum(x["size_mb"] for x in programs) / 1024, 2)
        
        results["windows_folders"] = analyze_windows_folder()
        
        winsxs = analyze_winsxs()
        if winsxs:
            results["winsxs"] = winsxs
        
        programdata = analyze_programdata()
        results["programdata_top_10"] = programdata[:10]
        results["programdata_total_gb"] = round(sum(x["size_mb"] for x in programdata) / 1024, 2)
        
        # Calculate total cleanable space
        system_files_total = sum(item["size_mb"] for item in results["system_files"])
        windows_cleanable = sum(
            item["size_mb"] for item in results["windows_folders"] 
            if item.get("safe_to_clean", False)
        )
        
        results["cleanup_opportunities"] = {
            "system_files_gb": round(system_files_total / 1024, 2),
            "windows_cleanable_gb": round(windows_cleanable / 1024, 2),
            "recommendations": [
                "Clean AppData folders (especially cache and temp)",
                "Review and uninstall unused programs",
                "Clean Windows system folders",
                "Consider disabling hibernation if not used",
                "Run Disk Cleanup and DISM to clean WinSxS"
            ]
        }
    
    else:
        results["success"] = False
        results["error"] = "Unknown command"
    
    return json.dumps(results, indent=2)
