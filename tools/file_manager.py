import os
import shutil
from pathlib import Path

DOWNLOADS_PATH = r"C:\Users\VICTUS\Downloads"

def list_files(input=""):
    """List all files and folders in Downloads"""
    try:
        items = []
        for item in os.listdir(DOWNLOADS_PATH):
            full_path = os.path.join(DOWNLOADS_PATH, item)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else 0
            size_mb = size / (1024 * 1024)  # Convert to MB
            items.append({
                'name': item,
                'type': 'folder' if is_dir else 'file',
                'size_bytes': size,
                'size_mb': round(size_mb, 2),
                'path': full_path
            })
        
        # Sort by size
        items.sort(key=lambda x: x['size_bytes'], reverse=True)
        
        result = f"Files in {DOWNLOADS_PATH}:\n\n"
        for item in items:
            result += f"{item['name']} - {item['size_mb']} MB ({item['type']})\n"
        
        return result
    except Exception as e:
        return f"Error listing files: {str(e)}"

def read_file(input):
    """Read content of a text file"""
    try:
        filename = input.strip()
        file_path = os.path.join(DOWNLOADS_PATH, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def delete_file(input):
    """Delete a file or folder"""
    try:
        filename = input.strip()
        file_path = os.path.join(DOWNLOADS_PATH, filename)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        return f"Successfully deleted: {filename}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

def rename_file(input):
    """Rename a file or folder - format: old_name|new_name"""
    try:
        old_name, new_name = input.split('|')
        old_path = os.path.join(DOWNLOADS_PATH, old_name.strip())
        new_path = os.path.join(DOWNLOADS_PATH, new_name.strip())
        os.rename(old_path, new_path)
        return f"Successfully renamed '{old_name}' to '{new_name}'"
    except Exception as e:
        return f"Error renaming file: {str(e)}"

def copy_file(input):
    """Copy a file or folder to destination - format: filename|destination"""
    try:
        filename, destination = input.split('|')
        source = os.path.join(DOWNLOADS_PATH, filename.strip())
        dest = destination.strip()
        
        if os.path.isdir(source):
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)
        return f"Successfully copied '{filename}' to '{destination}'"
    except Exception as e:
        return f"Error copying file: {str(e)}"

def move_file(input):
    """Move (cut) a file or folder to destination - format: filename|destination"""
    try:
        filename, destination = input.split('|')
        source = os.path.join(DOWNLOADS_PATH, filename.strip())
        dest = destination.strip()
        shutil.move(source, dest)
        return f"Successfully moved '{filename}' to '{destination}'"
    except Exception as e:
        return f"Error moving file: {str(e)}"

def search_files(input):
    """Search files by pattern in Downloads"""
    try:
        pattern = input.strip()
        items = []
        for item in os.listdir(DOWNLOADS_PATH):
            if pattern.lower() in item.lower():
                full_path = os.path.join(DOWNLOADS_PATH, item)
                size = os.path.getsize(full_path) if not os.path.isdir(full_path) else 0
                items.append(f"{item} - {round(size/(1024*1024), 2)} MB")
        
        if items:
            return f"Found {len(items)} file(s):\n" + "\n".join(items)
        else:
            return "No files found matching pattern"
    except Exception as e:
        return f"Error searching files: {str(e)}"

def find_large_files(input="50"):
    """Find files larger than specified MB (default 50MB)"""
    try:
        threshold_mb = float(input) if input else 50.0
        large_files = []
        
        for item in os.listdir(DOWNLOADS_PATH):
            full_path = os.path.join(DOWNLOADS_PATH, item)
            if not os.path.isdir(full_path):
                size = os.path.getsize(full_path)
                size_mb = size / (1024 * 1024)
                if size_mb > threshold_mb:
                    large_files.append({
                        'name': item,
                        'size_mb': round(size_mb, 2),
                        'size_gb': round(size_mb / 1024, 2)
                    })
        
        large_files.sort(key=lambda x: x['size_mb'], reverse=True)
        
        if large_files:
            result = f"Found {len(large_files)} file(s) larger than {threshold_mb} MB:\n\n"
            for f in large_files:
                result += f"{f['name']}\n  Size: {f['size_mb']} MB ({f['size_gb']} GB)\n\n"
            return result
        else:
            return f"No files found larger than {threshold_mb} MB"
    except Exception as e:
        return f"Error finding large files: {str(e)}"
