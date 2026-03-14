"""
Safe C Drive Cleanup Script
Run this on Windows to delete safe temporary files
"""
import os
import shutil
from pathlib import Path

def delete_folder_contents(folder_path, description):
    """Safely delete contents of a folder"""
    try:
        if not os.path.exists(folder_path):
            print(f"[SKIP] {description}: Folder not found")
            return 0
        
        deleted_size = 0
        file_count = 0
        
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            try:
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    os.remove(item_path)
                    deleted_size += size
                    file_count += 1
                elif os.path.isdir(item_path):
                    size = sum(f.stat().st_size for f in Path(item_path).rglob('*') if f.is_file())
                    shutil.rmtree(item_path)
                    deleted_size += size
                    file_count += 1
            except PermissionError:
                continue
            except Exception as e:
                continue
        
        size_mb = deleted_size / (1024 * 1024)
        print(f"[SUCCESS] {description}: Deleted {file_count} items, freed {size_mb:.2f} MB")
        return deleted_size
    except Exception as e:
        print(f"[ERROR] {description}: {str(e)}")
        return 0

print("="*70)
print("SAFE C: DRIVE CLEANUP SCRIPT")
print("="*70)
print()
print("This script will delete ONLY safe temporary files:")
print("- User Temp files")
print("- Browser caches")
print("- Windows Web Cache")
print()

# Confirm
response = input("Do you want to proceed? (yes/no): ").strip().lower()
if response != "yes":
    print("Cleanup cancelled.")
    exit()

print()
print("Starting cleanup...")
print()

total_deleted = 0

# 1. User Temp
user_temp = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
total_deleted += delete_folder_contents(user_temp, "User Temp Files")

# 2. Chrome Cache
chrome_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache')
total_deleted += delete_folder_contents(chrome_cache, "Chrome Cache")

# 3. Chrome Code Cache
chrome_code = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache')
total_deleted += delete_folder_contents(chrome_code, "Chrome Code Cache")

# 4. Edge Cache
edge_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache')
total_deleted += delete_folder_contents(edge_cache, "Edge Cache")

# 5. Edge Code Cache
edge_code = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Code Cache')
total_deleted += delete_folder_contents(edge_code, "Edge Code Cache")

# 6. Firefox Cache (multiple profiles)
firefox_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
if os.path.exists(firefox_base):
    for profile in os.listdir(firefox_base):
        profile_path = os.path.join(firefox_base, profile)
        if os.path.isdir(profile_path):
            cache_path = os.path.join(profile_path, 'cache2')
            if os.path.exists(cache_path):
                total_deleted += delete_folder_contents(cache_path, f"Firefox Cache ({profile})")

# 7. Windows Web Cache
web_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'WebCache')
total_deleted += delete_folder_contents(web_cache, "Windows Web Cache")

print()
print("="*70)
total_mb = total_deleted / (1024 * 1024)
total_gb = total_mb / 1024
print(f"CLEANUP COMPLETE!")
print(f"Total space freed: {total_mb:.2f} MB ({total_gb:.2f} GB)")
print("="*70)
print()
print("NOTE: The following were NOT deleted (requires manual action):")
print("- Recycle Bin (use: Empty Recycle Bin from desktop)")
print("- Downloads folder (review manually)")
print("- Windows Store Apps Cache (use Disk Cleanup tool)")
print()
