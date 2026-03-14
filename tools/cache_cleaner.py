"""
Cache Cleaner - Delete npm, uv, pip, and NuGet caches
"""
import os
import json
import shutil
from pathlib import Path

def delete_folder_contents(path, folder_name):
    """Delete folder contents handling long paths"""
    deleted = False
    error = None
    
    try:
        if os.path.exists(path):
            # Try normal deletion first
            try:
                shutil.rmtree(path)
                deleted = True
            except Exception as e:
                # If fails, try PowerShell for long paths
                try:
                    import subprocess
                    cmd = f'powershell -Command "Remove-Item -Path \\"{path}\\" -Recurse -Force"'
                    subprocess.run(cmd, shell=True, check=True, timeout=120)
                    deleted = True
                except Exception as e2:
                    error = str(e2)
        else:
            error = "Path does not exist"
    except Exception as e:
        error = str(e)
    
    return deleted, error

def run(input_str=""):
    """Delete all caches"""
    
    caches = [
        (r"C:\Users\VICTUS\AppData\Local\npm-cache", "npm-cache", 4.38),
        (r"C:\Users\VICTUS\AppData\Local\uv", "uv cache", 8.65),
        (r"C:\Users\VICTUS\AppData\Local\pip", "pip cache", 1.15),
        (r"C:\Users\VICTUS\AppData\Local\NuGet", "NuGet packages", 1.53),
    ]
    
    results = {
        "success": True,
        "deleted": [],
        "errors": [],
        "total_freed_gb": 0
    }
    
    for path, name, size_gb in caches:
        deleted, error = delete_folder_contents(path, name)
        
        if deleted:
            results["deleted"].append({
                "name": name,
                "path": path,
                "size_gb": size_gb
            })
            results["total_freed_gb"] += size_gb
        else:
            results["errors"].append({
                "name": name,
                "path": path,
                "error": error or "Unknown error"
            })
    
    results["total_freed_gb"] = round(results["total_freed_gb"], 2)
    
    return json.dumps(results, indent=2)
