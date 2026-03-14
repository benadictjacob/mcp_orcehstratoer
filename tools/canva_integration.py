import requests
import json
import os

# Canva API Configuration
CANVA_API_BASE = "https://api.canva.com/rest/v1"

def run(input_text: str) -> str:
    """
    Canva API Integration
    
    Setup Instructions:
    1. Go to https://www.canva.com/developers/
    2. Create an app to get your API key
    3. Set environment variable: CANVA_API_KEY=your_api_key
    
    Commands:
    - setup <api_key> : Set your Canva API key
    - check_auth : Check if API key is configured
    - list_designs : List your Canva designs
    - get_design <design_id> : Get details of a specific design
    - create_design <name> : Create a new design
    - export_design <design_id> <format> : Export design (png, jpg, pdf)
    - search_templates <query> : Search for templates
    - get_user : Get current user information
    """
    
    parts = input_text.strip().split(maxsplit=1)
    
    if not parts:
        return """Canva API Integration
        
Setup Instructions:
1. Go to https://www.canva.com/developers/
2. Create an app and get your API key
3. Use: setup <api_key>

Available commands:
- setup <api_key> : Configure your Canva API key
- check_auth : Verify authentication
- list_designs : List your designs
- get_design <design_id> : Get design details
- create_design <name> : Create new design
- export_design <design_id> <format> : Export (png/jpg/pdf)
- search_templates <query> : Search templates
- get_user : Get user info

Note: You need a Canva API key from https://www.canva.com/developers/"""
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    try:
        if command == "setup":
            if not args:
                return "Error: Please provide API key\nUsage: setup <api_key>"
            
            # Save API key to environment (temporary for this session)
            os.environ['CANVA_API_KEY'] = args
            
            # Also save to a local config file for persistence
            config = {"api_key": args}
            with open("canva_config.json", "w") as f:
                json.dump(config, f)
            
            return "SUCCESS: Canva API key configured!\nYou can now use other commands."
        
        # Load API key
        api_key = os.environ.get('CANVA_API_KEY')
        
        if not api_key:
            # Try loading from config file
            try:
                with open("canva_config.json", "r") as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
                    if api_key:
                        os.environ['CANVA_API_KEY'] = api_key
            except FileNotFoundError:
                pass
        
        if not api_key and command != "check_auth":
            return """Error: Canva API key not configured!

Setup Instructions:
1. Go to https://www.canva.com/developers/
2. Create an app and get your API key
3. Run: setup <your_api_key>"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if command == "check_auth":
            if not api_key:
                return "Not authenticated. Please run: setup <api_key>"
            
            response = requests.get(f"{CANVA_API_BASE}/users/me", headers=headers)
            
            if response.status_code == 200:
                return "SUCCESS: Canva API is properly configured!"
            else:
                return f"FAILED: Authentication failed\nStatus: {response.status_code}\nMessage: {response.text}"
        
        elif command == "get_user":
            response = requests.get(f"{CANVA_API_BASE}/users/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return f"User Information:\n{json.dumps(user_data, indent=2)}"
            else:
                return f"Error: {response.status_code}\n{response.text}"
        
        elif command == "list_designs":
            response = requests.get(f"{CANVA_API_BASE}/designs", headers=headers)
            
            if response.status_code == 200:
                designs = response.json()
                return f"Your Designs:\n{json.dumps(designs, indent=2)}"
            else:
                return f"Error: {response.status_code}\n{response.text}"
        
        elif command == "get_design":
            if not args:
                return "Error: Please provide design_id\nUsage: get_design <design_id>"
            
            design_id = args.strip()
            response = requests.get(f"{CANVA_API_BASE}/designs/{design_id}", headers=headers)
            
            if response.status_code == 200:
                design = response.json()
                return f"Design Details:\n{json.dumps(design, indent=2)}"
            else:
                return f"Error: {response.status_code}\n{response.text}"
        
        elif command == "create_design":
            if not args:
                return "Error: Please provide design name\nUsage: create_design <name>"
            
            data = {
                "design_type": "Presentation",
                "title": args.strip()
            }
            
            response = requests.post(
                f"{CANVA_API_BASE}/designs",
                headers=headers,
                json=data
            )
            
            if response.status_code in [200, 201]:
                design = response.json()
                return f"SUCCESS: Design created!\n{json.dumps(design, indent=2)}"
            else:
                return f"Error: {response.status_code}\n{response.text}"
        
        elif command == "export_design":
            parts = args.split()
            if len(parts) < 2:
                return "Error: Please provide design_id and format\nUsage: export_design <design_id> <png|jpg|pdf>"
            
            design_id = parts[0]
            export_format = parts[1].lower()
            
            data = {
                "format": export_format
            }
            
            response = requests.post(
                f"{CANVA_API_BASE}/designs/{design_id}/export",
                headers=headers,
                json=data
            )
            
            if response.status_code in [200, 201, 202]:
                export_data = response.json()
                return f"Export initiated!\n{json.dumps(export_data, indent=2)}"
            else:
                return f"Error: {response.status_code}\n{response.text}"
        
        elif command == "search_templates":
            if not args:
                return "Error: Please provide search query\nUsage: search_templates <query>"
            
            params = {
                "query": args.strip()
            }
            
            response = requests.get(
                f"{CANVA_API_BASE}/templates",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                templates = response.json()
                return f"Templates:\n{json.dumps(templates, indent=2)}"
            else:
                return f"Error: {response.status_code}\n{response.text}"
        
        else:
            return f"Unknown command: {command}\n\nRun without arguments to see available commands"
    
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
