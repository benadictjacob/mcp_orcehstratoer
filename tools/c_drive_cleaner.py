"""
C Drive Cleaner - Delete safe temporary and cache files
"""
import os
import json
import shutil
from pathlib import Path

def delete_folder_contents(folder_path):
    """Delete all contents of a folder"""
    deleted_size = 0
    file_count = 0
    
    try:
        if not os.path.exists(folder_path):
            return 0, 0
        
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            try:
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    os.remove(item_path)
                    deleted_size += size
                    file_count += 1
                elif os.path.isdir(item_path):
                    # Calculate size before deleting
                    for dirpath, dirnames, filenames in os.walk(item_path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                deleted_size += os.path.getsize(fp)
                            except:
                                pass
                    shutil.rmtree(item_path, ignore_errors=True)
                    file_count += 1
            except PermissionError:
                continue
            except Exception:
                continue
        
        return deleted_size, file_count
    except Exception:
        return 0, 0

def empty_recycle_bin():
    """Empty the recycle bin"""
    try:
        import ctypes
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0001 | 0x0002 | 0x0004)
        return True
    except:
        return False

def run(input_str=""):
    """Main cleanup function"""
    
    command = input_str.lower().strip()
    
    if not command or command == "help":
        return json.dumps({
            "commands": [
                "safe - Delete only 100% safe files (temp, cache)",
                "temp - Delete temporary files only",
                "cache - Delete browser caches only",
                "recycle - Empty recycle bin",
                "all - Delete all safe files including recycle bin"
            ],
            "warning": "This will permanently delete files!",
            "usage": "Use: run_capability with name='c_drive_cleanup' and input='safe'"
        }, indent=2)
    
    results = {
        "success": True,
        "command": command,
        "deleted_items": [],
        "errors": []
    }
    
    total_deleted_size = 0
    total_files_deleted = 0
    
    if command in ["safe", "temp", "all"]:
        # Delete user temp files
        try:
            user_temp = Path(os.environ.get('LOCALAPPDATA', '')) / "Temp"
            if user_temp.exists():
                size, count = delete_folder_contents(str(user_temp))
                if size > 0:
                    total_deleted_size += size
                    total_files_deleted += count
                    results["deleted_items"].append({
                        "type": "User Temp",
                        "path": str(user_temp),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "files_deleted": count
                    })
        except Exception as e:
            results["errors"].append(f"User Temp: {str(e)}")
        
        # Delete Windows Temp
        try:
            win_temp = Path(r"C:\Windows\Temp")
            if win_temp.exists():
                size, count = delete_folder_contents(str(win_temp))
                if size > 0:
                    total_deleted_size += size
                    total_files_deleted += count
                    results["deleted_items"].append({
                        "type": "Windows Temp",
                        "path": str(win_temp),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "files_deleted": count
                    })
        except Exception as e:
            results["errors"].append(f"Windows Temp: {str(e)}")
    
    if command in ["safe", "cache", "all"]:
        # Delete Chrome Cache
        try:
            chrome_cache = Path(os.environ.get('LOCALAPPDATA', '')) / "Google" / "Chrome" / "User Data" / "Default" / "Cache"
            if chrome_cache.exists():
                size, count = delete_folder_contents(str(chrome_cache))
                if size > 0:
                    total_deleted_size += size
                    total_files_deleted += count
                    results["deleted_items"].append({
                        "type": "Chrome Cache",
                        "path": str(chrome_cache),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "files_deleted": count
                    })
        except Exception as e:
            results["errors"].append(f"Chrome Cache: {str(e)}")
        
        # Delete Chrome Code Cache
        try:
            chrome_code = Path(os.environ.get('LOCALAPPDATA', '')) / "Google" / "Chrome" / "User Data" / "Default" / "Code Cache"
            if chrome_code.exists():
                size, count = delete_folder_contents(str(chrome_code))
                if size > 0:
                    total_deleted_size += size
                    total_files_deleted += count
                    results["deleted_items"].append({
                        "type": "Chrome Code Cache",
                        "path": str(chrome_code),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "files_deleted": count
                    })
        except Exception as e:
            results["errors"].append(f"Chrome Code Cache: {str(e)}")
        
        # Delete Edge Cache
        try:
            edge_cache = Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache"
            if edge_cache.exists():
                size, count = delete_folder_contents(str(edge_cache))
                if size > 0:
                    total_deleted_size += size
                    total_files_deleted += count
                    results["deleted_items"].append({
                        "type": "Edge Cache",
                        "path": str(edge_cache),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "files_deleted": count
                    })
        except Exception as e:
            results["errors"].append(f"Edge Cache: {str(e)}")
        
        # Delete Edge Code Cache
        try:
            edge_code = Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache"
            if edge_code.exists():
                size, count = delete_folder_contents(str(edge_code))
                if size > 0:
                    total_deleted_size += size
                    total_files_deleted += count
                    results["deleted_items"].append({
                        "type": "Edge Code Cache",
                        "path": str(edge_code),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "files_deleted": count
                    })
        except Exception as e:
            results["errors"].append(f"Edge Code Cache: {str(e)}")
        
        # Delete Firefox Cache
        try:
            firefox_base = Path(os.environ.get('LOCALAPPDATA', '')) / "Mozilla" / "Firefox" / "Profiles"
            if firefox_base.exists():
                for profile in firefox_base.iterdir():
                    if profile.is_dir():
                        cache_path = profile / "cache2"
                        if cache_path.exists():
                            size, count = delete_folder_contents(str(cache_path))
                            if size > 0:
                                total_deleted_size += size
                                total_files_deleted += count
                                results["deleted_items"].append({
                                    "type": "Firefox Cache",
                                    "path": str(cache_path),
                                    "size_mb": round(size / (1024 * 1024), 2),
                                    "files_deleted": count
                                })
        except Exception as e:
            results["errors"].append(f"Firefox Cache: {str(e)}")
    
    if command in ["recycle", "all"]:
        # Empty Recycle Bin
        try:
            if empty_recycle_bin():
                results["deleted_items"].append({
                    "type": "Recycle Bin",
                    "path": r"C:\$Recycle.Bin",
                    "status": "Emptied successfully"
                })
            else:
                results["errors"].append("Recycle Bin: Could not empty (may need admin rights)")
        except Exception as e:
            results["errors"].append(f"Recycle Bin: {str(e)}")
    
    # Calculate totals
    results["total_space_freed_mb"] = round(total_deleted_size / (1024 * 1024), 2)
    results["total_space_freed_gb"] = round(total_deleted_size / (1024 * 1024 * 1024), 2)
    results["total_files_deleted"] = total_files_deleted
    results["items_processed"] = len(results["deleted_items"])
    
    if not results["deleted_items"]:
        results["message"] = "No files were deleted. Items may not exist or lack permissions."
    
    return json.dumps(results, indent=2)
