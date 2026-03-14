import requests
import json

def run(input_text: str) -> str:
    """
    Quote API Integration - NO AUTHENTICATION REQUIRED!
    Get inspirational quotes, jokes, facts, and more.
    
    Commands:
    - quote : Get random inspirational quote
    - quote <category> : Quote from category (motivational, success, life, etc)
    - joke : Get a random joke
    - fact : Get a random interesting fact
    - advice : Get random advice
    - affirmation : Get positive affirmation
    - kanye : Get a Kanye West quote
    """
    
    parts = input_text.strip().split(maxsplit=1)
    
    if not parts:
        return """Quote & Content APIs - NO LOGIN REQUIRED!

Available commands:
- quote : Random inspirational quote
- quote <category> : Category-specific quote
- joke : Random joke
- fact : Random fact
- advice : Random advice
- affirmation : Positive affirmation
- kanye : Kanye West quote

Example: quote
Example: joke
Example: fact"""
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    try:
        if command == "quote":
            if args:
                # Quote with specific category
                response = requests.get(f"https://api.quotable.io/random?tags={args}")
            else:
                # Random quote
                response = requests.get("https://api.quotable.io/random")
            
            if response.status_code == 200:
                data = response.json()
                return f'''"{data['content']}"

- {data['author']}

Tags: {', '.join(data.get('tags', []))}'''
            else:
                return f"Error fetching quote: {response.status_code}"
        
        elif command == "joke":
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            
            if response.status_code == 200:
                data = response.json()
                return f"""{data['setup']}

{data['punchline']}

Type: {data.get('type', 'general')}"""
            else:
                return f"Error fetching joke: {response.status_code}"
        
        elif command == "fact":
            response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
            
            if response.status_code == 200:
                data = response.json()
                return f"""Random Fact:

{data['text']}

Source: {data.get('source', 'Unknown')}"""
            else:
                return f"Error fetching fact: {response.status_code}"
        
        elif command == "advice":
            response = requests.get("https://api.adviceslip.com/advice")
            
            if response.status_code == 200:
                data = response.json()
                return f"""Advice:

{data['slip']['advice']}"""
            else:
                return f"Error fetching advice: {response.status_code}"
        
        elif command == "affirmation":
            response = requests.get("https://www.affirmations.dev/")
            
            if response.status_code == 200:
                data = response.json()
                return f"""Positive Affirmation:

{data['affirmation']}"""
            else:
                return f"Error fetching affirmation: {response.status_code}"
        
        elif command == "kanye":
            response = requests.get("https://api.kanye.rest/")
            
            if response.status_code == 200:
                data = response.json()
                return f'''Kanye says:

"{data['quote']}"

- Kanye West'''
            else:
                return f"Error fetching Kanye quote: {response.status_code}"
        
        else:
            return f"Unknown command: {command}\n\nRun without arguments to see available commands"
    
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
