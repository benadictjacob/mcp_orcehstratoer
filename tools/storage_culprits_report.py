"""
Storage Culprits Report - Show exactly what's eating your disk space
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

def run(input_str=""):
    """Generate storage culprits report"""
    
    # From our previous scans, compile the biggest culprits
    culprits = []
    
    # AppData folders
    appdata_items = [
        ("C:\\Users\\VICTUS\\AppData\\Local\\Programs", "Programs & Apps", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\Docker", "Docker Data", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\uv", "UV Python Cache", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\UiPathConnected", "UiPath Data", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\Microsoft", "Microsoft Apps Data", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\npm-cache", "NPM Cache", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\Android", "Android SDK", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\Packages", "Windows Store Apps", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\Google", "Google Apps Data", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\NuGet", "NuGet Packages", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\NVIDIA", "NVIDIA Data", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\Perplexity", "Perplexity App", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\pip", "PIP Cache", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Roaming\\Code", "VS Code Settings", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Roaming\\Antigravity", "Antigravity Data", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Roaming\\Notion", "Notion Data", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Roaming\\Cursor", "Cursor Settings", "AppData"),
        ("C:\\Users\\VICTUS\\AppData\\Local\\Postman", "Postman Data", "AppData"),
    ]
    
    # Program Files
    program_items = [
        ("C:\\Program Files\\Microsoft Office", "Microsoft Office", "Program"),
        ("C:\\Program Files\\Docker", "Docker Desktop", "Program"),
        ("C:\\Program Files\\Adobe", "Adobe Suite", "Program"),
        ("C:\\Program Files\\PostgreSQL", "PostgreSQL Database", "Program"),
        ("C:\\Program Files\\MySQL", "MySQL Database", "Program"),
        ("C:\\Program Files\\Blender Foundation", "Blender 3D", "Program"),
        ("C:\\Program Files\\Blue Prism Limited", "Blue Prism RPA", "Program"),
        ("C:\\Program Files\\cursor", "Cursor IDE", "Program"),
        ("C:\\Program Files\\BraveSoftware", "Brave Browser", "Program"),
        ("C:\\Program Files\\HP", "HP Software", "Program"),
    ]
    
    # User folders
    user_items = [
        ("C:\\Users\\VICTUS\\Downloads", "Downloads", "User Files"),
        ("C:\\Users\\VICTUS\\Documents", "Documents", "User Files"),
        ("C:\\Users\\VICTUS\\Videos", "Videos", "User Files"),
        ("C:\\Users\\VICTUS\\Pictures", "Pictures", "User Files"),
        ("C:\\Users\\VICTUS\\Desktop", "Desktop", "User Files"),
    ]
    
    all_items = appdata_items + program_items + user_items
    
    for path, name, category in all_items:
        if os.path.exists(path):
            size = get_folder_size(path)
            if size > 10:  # Only items > 10MB
                culprits.append({
                    "name": name,
                    "path": path,
                    "category": category,
                    "size_mb": round(size, 2),
                    "size_gb": round(size / 1024, 2),
                    "can_move_to_d": category in ["User Files", "AppData"] and name not in ["Programs & Apps"],
                    "safe_to_delete": name in ["NPM Cache", "UV Python Cache", "PIP Cache", "NuGet Packages"],
                    "requires_review": category == "Program" or name in ["Docker Data", "Android SDK", "UiPath Data"]
                })
    
    # Sort by size
    culprits.sort(key=lambda x: x["size_mb"], reverse=True)
    
    # Categorize
    moveable = [c for c in culprits if c["can_move_to_d"]]
    deletable = [c for c in culprits if c["safe_to_delete"]]
    review_needed = [c for c in culprits if c["requires_review"]]
    
    results = {
        "success": True,
        "all_culprits": culprits[:30],  # Top 30
        "total_analyzed_gb": round(sum(c["size_mb"] for c in culprits) / 1024, 2),
        
        "moveable_to_d_drive": {
            "items": moveable[:15],
            "total_gb": round(sum(c["size_mb"] for c in moveable) / 1024, 2),
            "count": len(moveable)
        },
        
        "safe_to_delete": {
            "items": deletable,
            "total_gb": round(sum(c["size_mb"] for c in deletable) / 1024, 2),
            "count": len(deletable)
        },
        
        "review_before_action": {
            "items": review_needed[:15],
            "total_gb": round(sum(c["size_mb"] for c in review_needed) / 1024, 2),
            "count": len(review_needed)
        },
        
        "recommendations": [
            "Move user files (Downloads, Documents, Videos) to D: drive",
            "Delete all cache folders (npm, uv, pip, NuGet)",
            "Uninstall unused programs (Docker, UiPath, Android SDK if not using)",
            "Keep system files and actively used programs on C:"
        ]
    }
    
    return json.dumps(results, indent=2)
