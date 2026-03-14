"""
Detailed Program and AppData Scanner
Lists ALL programs and AppData folders with sizes
"""
import os
import json
from pathlib import Path

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

def scan_program_files():
    """Scan both Program Files directories"""
    results = []
    
    paths = [
        (r"C:\Program Files", "Program Files"),
        (r"C:\Program Files (x86)", "Program Files (x86)")
    ]
    
    for base_path, location in paths:
        if not os.path.exists(base_path):
            continue
        
        try:
            items = list(Path(base_path).iterdir())
            for item in items:
                if item.is_dir():
                    size = get_folder_size(str(item))
                    results.append({
                        "name": item.name,
                        "location": location,
                        "path": str(item),
                        "size_mb": round(size, 2),
                        "size_gb": round(size / 1024, 2)
                    })
        except Exception as e:
            pass
    
    results.sort(key=lambda x: x["size_mb"], reverse=True)
    return results

def scan_appdata():
    """Scan AppData Local and Roaming"""
    results = []
    
    paths = [
        (r"C:\Users\VICTUS\AppData\Local", "AppData Local"),
        (r"C:\Users\VICTUS\AppData\Roaming", "AppData Roaming")
    ]
    
    for base_path, location in paths:
        if not os.path.exists(base_path):
            continue
        
        try:
            items = list(Path(base_path).iterdir())
            for item in items:
                if item.is_dir():
                    size = get_folder_size(str(item))
                    results.append({
                        "name": item.name,
                        "location": location,
                        "path": str(item),
                        "size_mb": round(size, 2),
                        "size_gb": round(size / 1024, 2)
                    })
        except Exception as e:
            pass
    
    results.sort(key=lambda x: x["size_mb"], reverse=True)
    return results

def run(input_str=""):
    """Main entry point"""
    
    command = input_str.lower().strip()
    
    if not command or command == "help":
        return json.dumps({
            "commands": [
                "programs - List all Program Files",
                "appdata - List all AppData folders",
                "both - List both (all programs and appdata)",
                "top50 - Top 50 largest items from both"
            ]
        }, indent=2)
    
    results = {"success": True, "command": command}
    
    if command == "programs":
        programs = scan_program_files()
        results["programs"] = programs
        results["total_count"] = len(programs)
        results["total_size_gb"] = round(sum(p["size_mb"] for p in programs) / 1024, 2)
    
    elif command == "appdata":
        appdata = scan_appdata()
        results["appdata"] = appdata
        results["total_count"] = len(appdata)
        results["total_size_gb"] = round(sum(a["size_mb"] for a in appdata) / 1024, 2)
    
    elif command == "both":
        programs = scan_program_files()
        appdata = scan_appdata()
        
        results["programs"] = programs
        results["programs_count"] = len(programs)
        results["programs_total_gb"] = round(sum(p["size_mb"] for p in programs) / 1024, 2)
        
        results["appdata"] = appdata
        results["appdata_count"] = len(appdata)
        results["appdata_total_gb"] = round(sum(a["size_mb"] for a in appdata) / 1024, 2)
        
        results["grand_total_gb"] = results["programs_total_gb"] + results["appdata_total_gb"]
    
    elif command == "top50":
        programs = scan_program_files()
        appdata = scan_appdata()
        
        # Combine and sort
        all_items = []
        for p in programs:
            p["type"] = "Program"
            all_items.append(p)
        
        for a in appdata:
            a["type"] = "AppData"
            all_items.append(a)
        
        all_items.sort(key=lambda x: x["size_mb"], reverse=True)
        
        results["top_50_items"] = all_items[:50]
        results["total_items_scanned"] = len(all_items)
        results["top_50_total_gb"] = round(sum(i["size_mb"] for i in all_items[:50]) / 1024, 2)
    
    else:
        results["success"] = False
        results["error"] = "Unknown command"
    
    return json.dumps(results, indent=2)
