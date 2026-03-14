import requests
import json
import random

def run(input_text: str) -> str:
    """
    Random Quotes Generator (No API Key Required!)
    
    Commands:
    - random : Get a random quote
    - category <cat> : Get quote by category (inspirational, success, life, etc)
    - author <name> : Get quotes by author
    - daily : Get quote of the day
    """
    
    parts = input_text.strip().split(maxsplit=1)
    
    if not parts:
        return """Random Quotes Generator (No Authentication!)

Available commands:
- random : Get a random quote
- category <cat> : Quote by category
- author <name> : Quotes by author
- daily : Quote of the day

Examples:
  random
  category success
  author Einstein
  daily"""
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    try:
        if command == "random":
            # Using quotable.io API - free, no key needed
            url = "https://api.quotable.io/random"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return f'"{data["content"]}"\n\n- {data["author"]}'
            else:
                return f"Error: Could not fetch quote\nStatus: {response.status_code}"
        
        elif command == "category":
            if not args:
                return "Error: Please provide a category\nAvailable: inspirational, success, life, wisdom, friendship"
            
            url = f"https://api.quotable.io/random?tags={args}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return f'Category: {args}\n\n"{data["content"]}"\n\n- {data["author"]}'
            else:
                return f"Error: Could not fetch quote\nStatus: {response.status_code}"
        
        elif command == "author":
            if not args:
                return "Error: Please provide an author name"
            
            url = f"https://api.quotable.io/random?author={args}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return f'"{data["content"]}"\n\n- {data["author"]}'
            else:
                return f"Error: Could not find quotes by that author\nStatus: {response.status_code}"
        
        elif command == "daily":
            # Get today's "quote of the day" by using a consistent seed
            url = "https://api.quotable.io/random?maxLength=150"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return f'Quote of the Day:\n\n"{data["content"]}"\n\n- {data["author"]}'
            else:
                return f"Error: Could not fetch quote\nStatus: {response.status_code}"
        
        else:
            return f"Unknown command: {command}\n\nRun without arguments to see available commands"
    
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
