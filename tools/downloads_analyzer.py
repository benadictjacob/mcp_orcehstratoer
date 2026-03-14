"""
Downloads Analyzer - Analyze Downloads folder for deletable files
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

def analyze_downloads():
    """Analyze Downloads folder and categorize files"""
    
    downloads_path = Path(r"C:\Users\VICTUS\Downloads")
    
    if not downloads_path.exists():
        return {"error": "Downloads folder not found"}
    
    results = {
        "path": str(downloads_path),
        "files": [],
        "categories": {
            "installers": [],
            "compressed": [],
            "documents": [],
            "images": [],
            "videos": [],
            "old_files": [],
            "large_files": [],
            "other": []
        }
    }
    
    # File extensions by category
    installer_exts = {'.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'}
    compressed_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
    doc_exts = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
    video_exts = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
    
    current_time = datetime.now()
    old_threshold = current_time - timedelta(days=30)  # Files older than 30 days
    
    try:
        for item in downloads_path.iterdir():
            try:
                if item.is_file():
                    size = item.stat().st_size
                    size_mb = size / (1024 * 1024)
                    modified = datetime.fromtimestamp(item.stat().st_mtime)
                    age_days = (current_time - modified).days
                    
                    file_info = {
                        "name": item.name,
                        "path": str(item),
                        "size_mb": round(size_mb, 2),
                        "modified": modified.strftime('%Y-%m-%d %H:%M'),
                        "age_days": age_days,
                        "extension": item.suffix.lower()
                    }
                    
                    results["files"].append(file_info)
                    
                    # Categorize by type
                    if item.suffix.lower() in installer_exts:
                        results["categories"]["installers"].append(file_info)
                    elif item.suffix.lower() in compressed_exts:
                        results["categories"]["compressed"].append(file_info)
                    elif item.suffix.lower() in doc_exts:
                        results["categories"]["documents"].append(file_info)
                    elif item.suffix.lower() in image_exts:
                        results["categories"]["images"].append(file_info)
                    elif item.suffix.lower() in video_exts:
                        results["categories"]["videos"].append(file_info)
                    else:
                        results["categories"]["other"].append(file_info)
                    
                    # Mark old files
                    if modified < old_threshold:
                        results["categories"]["old_files"].append(file_info)
                    
                    # Mark large files (>100MB)
                    if size_mb > 100:
                        results["categories"]["large_files"].append(file_info)
                
                elif item.is_dir():
                    # Calculate folder size
                    folder_size = 0
                    for dirpath, dirnames, filenames in os.walk(item):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                folder_size += os.path.getsize(fp)
                            except:
                                pass
                    
                    folder_size_mb = folder_size / (1024 * 1024)
                    modified = datetime.fromtimestamp(item.stat().st_mtime)
                    age_days = (current_time - modified).days
                    
                    folder_info = {
                        "name": item.name,
                        "path": str(item),
                        "size_mb": round(folder_size_mb, 2),
                        "modified": modified.strftime('%Y-%m-%d %H:%M'),
                        "age_days": age_days,
                        "type": "folder"
                    }
                    
                    results["files"].append(folder_info)
                    
                    if modified < old_threshold:
                        results["categories"]["old_files"].append(folder_info)
                    
                    if folder_size_mb > 100:
                        results["categories"]["large_files"].append(folder_info)
            
            except Exception as e:
                continue
        
        # Sort files by size (largest first)
        results["files"].sort(key=lambda x: x["size_mb"], reverse=True)
        for category in results["categories"]:
            results["categories"][category].sort(key=lambda x: x["size_mb"], reverse=True)
        
        # Calculate statistics
        total_size = sum(f["size_mb"] for f in results["files"])
        results["stats"] = {
            "total_files": len(results["files"]),
            "total_size_mb": round(total_size, 2),
            "total_size_gb": round(total_size / 1024, 2),
            "installers_count": len(results["categories"]["installers"]),
            "installers_size_mb": round(sum(f["size_mb"] for f in results["categories"]["installers"]), 2),
            "compressed_count": len(results["categories"]["compressed"]),
            "compressed_size_mb": round(sum(f["size_mb"] for f in results["categories"]["compressed"]), 2),
            "old_files_count": len(results["categories"]["old_files"]),
            "old_files_size_mb": round(sum(f["size_mb"] for f in results["categories"]["old_files"]), 2),
            "large_files_count": len(results["categories"]["large_files"]),
            "large_files_size_mb": round(sum(f["size_mb"] for f in results["categories"]["large_files"]), 2)
        }
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

def run(input_str=""):
    """Main entry point"""
    
    command = input_str.lower().strip()
    
    if command == "help" or not command:
        return json.dumps({
            "commands": [
                "analyze - Full analysis of Downloads folder",
                "installers - Show installer files only",
                "compressed - Show compressed files only",
                "old - Show files older than 30 days",
                "large - Show files larger than 100MB",
                "top20 - Show top 20 largest files"
            ]
        }, indent=2)
    
    results = analyze_downloads()
    
    if "error" in results:
        return json.dumps(results, indent=2)
    
    if command == "analyze":
        return json.dumps(results, indent=2)
    
    elif command == "installers":
        return json.dumps({
            "category": "Installers",
            "count": len(results["categories"]["installers"]),
            "total_size_mb": round(sum(f["size_mb"] for f in results["categories"]["installers"]), 2),
            "files": results["categories"]["installers"]
        }, indent=2)
    
    elif command == "compressed":
        return json.dumps({
            "category": "Compressed Files",
            "count": len(results["categories"]["compressed"]),
            "total_size_mb": round(sum(f["size_mb"] for f in results["categories"]["compressed"]), 2),
            "files": results["categories"]["compressed"]
        }, indent=2)
    
    elif command == "old":
        return json.dumps({
            "category": "Old Files (>30 days)",
            "count": len(results["categories"]["old_files"]),
            "total_size_mb": round(sum(f["size_mb"] for f in results["categories"]["old_files"]), 2),
            "files": results["categories"]["old_files"]
        }, indent=2)
    
    elif command == "large":
        return json.dumps({
            "category": "Large Files (>100MB)",
            "count": len(results["categories"]["large_files"]),
            "total_size_mb": round(sum(f["size_mb"] for f in results["categories"]["large_files"]), 2),
            "files": results["categories"]["large_files"]
        }, indent=2)
    
    elif command == "top20":
        return json.dumps({
            "category": "Top 20 Largest Files/Folders",
            "files": results["files"][:20]
        }, indent=2)
    
    else:
        return json.dumps({"error": "Unknown command. Use 'help' for available commands."}, indent=2)
