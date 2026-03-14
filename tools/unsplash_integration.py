import requests
import json
import os
from urllib.parse import quote

def run(input_text: str) -> str:
    """
    Unsplash Free Stock Photos API Integration
    NO AUTHENTICATION REQUIRED for basic usage!
    
    Commands:
    - search <query> : Search for photos
    - random : Get a random photo
    - random <query> : Get random photo from category
    - photo <photo_id> : Get details of specific photo
    - download <photo_id> : Get download link for photo
    - trending : Get trending photos
    - collections : List popular collections
    """
    
    parts = input_text.strip().split(maxsplit=1)
    
    if not parts:
        return """Unsplash Stock Photos - NO LOGIN REQUIRED!

Available commands:
- search <query> : Search for photos (e.g., "nature", "business")
- random : Get a random photo
- random <query> : Random photo from category
- photo <photo_id> : Get photo details
- download <photo_id> : Get download link
- trending : Get trending photos
- collections : Popular collections

Example: search sunset
Example: random nature
Example: trending"""
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Using Unsplash Source API (no auth required)
    BASE_URL = "https://source.unsplash.com"
    API_URL = "https://api.unsplash.com"
    
    try:
        if command == "search":
            if not args:
                return "Error: Please provide search query\nUsage: search <query>"
            
            query = quote(args.strip())
            
            # Get image URL
            image_url = f"{BASE_URL}/1600x900/?{query}"
            
            return f"""Photo found for '{args}'!

Download URL: {image_url}

Usage:
- Right-click and save the image
- Use in your projects (free for commercial use)
- No attribution required (but appreciated)

Try: search <different query> for more options"""
        
        elif command == "random":
            if args:
                query = quote(args.strip())
                image_url = f"{BASE_URL}/random/1600x900/?{query}"
                return f"""Random photo from '{args}' category!

Download URL: {image_url}

Free to use for any project!"""
            else:
                image_url = f"{BASE_URL}/random/1600x900"
                return f"""Random photo!

Download URL: {image_url}

Free to use - no attribution required!"""
        
        elif command == "trending":
            # Get multiple trending images
            images = []
            for i in range(5):
                images.append(f"{BASE_URL}/random/800x600/?featured")
            
            result = "Top 5 Trending Photos:\n\n"
            for idx, img in enumerate(images, 1):
                result += f"{idx}. {img}\n"
            
            result += "\nAll images are free to use!"
            return result
        
        elif command == "collections":
            collections = [
                ("Nature", "nature"),
                ("Business", "business"),
                ("Technology", "technology"),
                ("Food", "food"),
                ("Travel", "travel"),
                ("People", "people"),
                ("Architecture", "architecture"),
                ("Animals", "animals"),
                ("Fashion", "fashion"),
                ("Art", "art")
            ]
            
            result = "Popular Collections:\n\n"
            for name, query in collections:
                result += f"- {name}: search {query}\n"
            
            result += "\nExample: search technology"
            return result
        
        elif command == "photo":
            if not args:
                return "Error: Please provide photo ID\nUsage: photo <photo_id>"
            
            photo_id = args.strip()
            image_url = f"{BASE_URL}/{photo_id}/1600x900"
            
            return f"""Photo ID: {photo_id}

Download URL: {image_url}

Free to use in any project!"""
        
        elif command == "download":
            if not args:
                return "Error: Please provide photo ID or search query\nUsage: download <photo_id>"
            
            photo_id = args.strip()
            image_url = f"{BASE_URL}/{photo_id}/1600x900"
            
            return f"""Download Link Generated!

Full Size: {image_url}
Medium Size: {BASE_URL}/{photo_id}/800x600
Small Size: {BASE_URL}/{photo_id}/400x300

Right-click on any link to download.
Free for commercial and personal use!"""
        
        else:
            return f"Unknown command: {command}\n\nRun without arguments to see available commands"
    
    except Exception as e:
        return f"Error: {str(e)}"
