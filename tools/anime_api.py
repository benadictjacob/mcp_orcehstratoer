"""
Anime API Integration using Jikan API (MyAnimeList)
No authentication required
"""

import requests
import json

def run(input_data: str = "") -> str:
    """
    Main entry point for anime API capability
    
    Commands:
    - search <query>: Search for anime by name
    - top [limit]: Get top anime (default limit 10)
    - details <id>: Get detailed info about anime by ID
    - seasonal: Get current season's anime
    - random: Get random anime
    - help: Show available commands
    """
    
    if not input_data or input_data.strip() == "help":
        return """
Anime API Commands (Powered by Jikan/MyAnimeList):

[TV] search <query>     - Search for anime by name
   Example: search naruto

[TOP] top [limit]       - Get top rated anime (default 10)
   Example: top 5

[INFO] details <id>     - Get detailed anime info by MAL ID
   Example: details 20

[CAL] seasonal          - Get current season's anime

[DICE] random           - Get a random anime

[?] help                - Show this help message

Note: All data from MyAnimeList via Jikan API
"""
    
    parts = input_data.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    BASE_URL = "https://api.jikan.moe/v4"
    
    try:
        if command == "search":
            if not args:
                return "ERROR: Please provide a search query. Example: search naruto"
            
            response = requests.get(f"{BASE_URL}/anime", params={"q": args, "limit": 10})
            response.raise_for_status()
            data = response.json()
            
            if not data.get("data"):
                return f"No results found for '{args}'"
            
            results = []
            for anime in data["data"][:10]:
                synopsis = anime.get('synopsis') or 'No synopsis available'
                results.append(
                    f"[TV] {anime['title']}\n"
                    f"   ID: {anime['mal_id']} | Score: {anime.get('score', 'N/A')} STAR\n"
                    f"   Type: {anime.get('type', 'N/A')} | Episodes: {anime.get('episodes', 'N/A')}\n"
                    f"   {synopsis[:150]}..."
                )
            
            return f"Search results for '{args}':\n\n" + "\n\n".join(results)
        
        elif command == "top":
            limit = int(args) if args.isdigit() else 10
            limit = min(limit, 25)
            
            response = requests.get(f"{BASE_URL}/top/anime", params={"limit": limit})
            response.raise_for_status()
            data = response.json()
            
            results = []
            for i, anime in enumerate(data["data"], 1):
                results.append(
                    f"{i}. {anime['title']}\n"
                    f"   Score: {anime.get('score', 'N/A')} STAR | "
                    f"Rank: #{anime.get('rank', 'N/A')} | "
                    f"Type: {anime.get('type', 'N/A')}"
                )
            
            return f"[TOP] Top {limit} Anime:\n\n" + "\n\n".join(results)
        
        elif command == "details":
            if not args.isdigit():
                return "ERROR: Please provide a valid anime ID. Example: details 20"
            
            response = requests.get(f"{BASE_URL}/anime/{args}/full")
            response.raise_for_status()
            data = response.json()["data"]
            
            genres = ", ".join([g["name"] for g in data.get("genres", [])])
            studios = ", ".join([s["name"] for s in data.get("studios", [])])
            synopsis = data.get('synopsis') or 'No synopsis available'
            
            return f"""
[TV] {data['title']} ({data.get('title_japanese', 'N/A')})

[STAR] Score: {data.get('score', 'N/A')}/10 (Rank #{data.get('rank', 'N/A')})
[CHART] Popularity: #{data.get('popularity', 'N/A')}
[USERS] Members: {data.get('members', 'N/A'):,}

[DATE] Aired: {data.get('aired', {}).get('string', 'N/A')}
[TV] Type: {data.get('type', 'N/A')} | Episodes: {data.get('episodes', 'N/A')}
[TIME] Duration: {data.get('duration', 'N/A')}
[GENRE] Genres: {genres or 'N/A'}
[STUDIO] Studios: {studios or 'N/A'}
[RATING] Rating: {data.get('rating', 'N/A')}

[BOOK] Synopsis:
{synopsis}

[LINK] MyAnimeList: {data.get('url', 'N/A')}
"""
        
        elif command == "seasonal":
            response = requests.get(f"{BASE_URL}/seasons/now")
            response.raise_for_status()
            data = response.json()
            
            results = []
            for anime in data["data"][:15]:
                results.append(
                    f"[TV] {anime['title']}\n"
                    f"   Score: {anime.get('score', 'N/A')} STAR | "
                    f"Type: {anime.get('type', 'N/A')} | "
                    f"Episodes: {anime.get('episodes', 'N/A')}"
                )
            
            season = data.get("season", "Current")
            year = data.get("year", "")
            return f"[CALENDAR] {season.title()} {year} Anime:\n\n" + "\n\n".join(results)
        
        elif command == "random":
            response = requests.get(f"{BASE_URL}/random/anime")
            response.raise_for_status()
            data = response.json()["data"]
            
            genres = ", ".join([g["name"] for g in data.get("genres", [])])
            synopsis = data.get('synopsis') or 'No synopsis available'
            
            return f"""
[DICE] Random Anime:

[TV] {data['title']}
[STAR] Score: {data.get('score', 'N/A')}/10
[TV] Type: {data.get('type', 'N/A')} | Episodes: {data.get('episodes', 'N/A')}
[GENRE] Genres: {genres or 'N/A'}

[BOOK] {synopsis[:300]}...

[LINK] {data.get('url', 'N/A')}
"""
        
        else:
            return f"ERROR: Unknown command: {command}\n\nUse 'help' to see available commands"
    
    except requests.exceptions.RequestException as e:
        return f"ERROR API: {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"
