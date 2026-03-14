"""
C Drive Manager - Analyze and find unnecessary files
"""
import os
import json
from pathlib import Path

def get_size_mb(path):
    """Get size in MB"""
    try:
        if os.path.isfile(path):
            return os.path.getsize(path) / (1024 * 1024)
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except:
                    pass
        return total / (1024 * 1024)
    except:
        return 0

def run(command=""):
    """Main entry point"""
    cmd = command.lower().strip()
    
    if not cmd or cmd == "help":
        return """C Drive Manager Commands:
- analyze : Full analysis of unnecessary files
- temp : Find temporary files
- cache : Find cache files  
- recycle : Check Recycle Bin
- downloads : Analyze Downloads folders
- large : Find large files (>100MB)
"""
    
    results = []
    
    if cmd == "analyze":
        # Temp files
        temp_dirs = [r"C:\Windows\Temp", r"C:\Temp"]
        for td in temp_dirs:
            if os.path.exists(td):
                size = get_size_mb(td)
                if size > 10:
                    results.append(f"[TEMP] {td}: {size:.1f} MB (Safe to delete)")
        
        # User temp
        try:
            for user in Path(r"C:\Users").iterdir():
                if user.is_dir():
                    temp = user / "AppData" / "Local" / "Temp"
                    if temp.exists():
                        size = get_size_mb(str(temp))
                        if size > 10:
                            results.append(f"[TEMP] {temp}: {size:.1f} MB (User temp - Safe to delete)")
        except:
            pass
        
        # Recycle Bin
        rb = r"C:\$Recycle.Bin"
        if os.path.exists(rb):
            size = get_size_mb(rb)
            if size > 0:
                results.append(f"[RECYCLE] {rb}: {size:.1f} MB (Empty recycle bin)")
        
        # Windows.old
        old = r"C:\Windows.old"
        if os.path.exists(old):
            size = get_size_mb(old)
            results.append(f"[OLD] {old}: {size:.1f} MB (Old Windows - Can delete)")
        
        # Downloads
        try:
            for user in Path(r"C:\Users").iterdir():
                if user.is_dir():
                    dl = user / "Downloads"
                    if dl.exists():
                        size = get_size_mb(str(dl))
                        if size > 100:
                            results.append(f"[DOWNLOADS] {dl}: {size:.1f} MB (Review old downloads)")
        except:
            pass
        
        # Windows Update cache
        upd = r"C:\Windows\SoftwareDistribution\Download"
        if os.path.exists(upd):
            size = get_size_mb(upd)
            if size > 100:
                results.append(f"[CACHE] {upd}: {size:.1f} MB (Update cache)")
        
    elif cmd == "temp":
        temp_dirs = [r"C:\Windows\Temp", r"C:\Temp"]
        for td in temp_dirs:
            if os.path.exists(td):
                size = get_size_mb(td)
                results.append(f"{td}: {size:.1f} MB")
        try:
            for user in Path(r"C:\Users").iterdir():
                if user.is_dir():
                    temp = user / "AppData" / "Local" / "Temp"
                    if temp.exists():
                        size = get_size_mb(str(temp))
                        results.append(f"{temp}: {size:.1f} MB")
        except:
            pass
        
    elif cmd == "recycle":
        rb = r"C:\$Recycle.Bin"
        if os.path.exists(rb):
            size = get_size_mb(rb)
            results.append(f"Recycle Bin: {size:.1f} MB")
    
    elif cmd == "downloads":
        try:
            for user in Path(r"C:\Users").iterdir():
                if user.is_dir():
                    dl = user / "Downloads"
                    if dl.exists():
                        size = get_size_mb(str(dl))
                        results.append(f"{dl}: {size:.1f} MB")
        except:
            pass
    
    elif cmd == "cache":
        cache_dirs = [
            r"C:\Windows\SoftwareDistribution\Download",
            r"C:\ProgramData\Package Cache"
        ]
        for cd in cache_dirs:
            if os.path.exists(cd):
                size = get_size_mb(cd)
                if size > 10:
                    results.append(f"{cd}: {size:.1f} MB")
    
    elif cmd == "large":
        results.append("Searching for large files (>100MB)...")
        results.append("Note: For detailed large file analysis, use Windows Storage Sense or third-party tools like TreeSize")
    
    if results:
        return "\n".join(results)
    else:
        return "No significant unnecessary files found or unable to access C: drive."
