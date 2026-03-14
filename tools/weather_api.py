import requests
import json

def run(input_text: str) -> str:
    """
    Weather & Location API - NO AUTHENTICATION REQUIRED!
    
    Commands:
    - weather <city> : Get current weather for city
    - forecast <city> : Get 5-day forecast
    - ip : Get your current IP and location
    - time <city> : Get current time in city
    - timezone <city> : Get timezone info
    """
    
    parts = input_text.strip().split(maxsplit=1)
    
    if not parts:
        return """Weather & Location APIs - NO LOGIN REQUIRED!

Available commands:
- weather <city> : Current weather (e.g., "London", "New York")
- forecast <city> : 5-day forecast
- ip : Your IP and location info
- time <city> : Current time in city
- timezone <city> : Timezone information

Example: weather London
Example: ip
Example: time Tokyo"""
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    try:
        if command == "weather":
            if not args:
                return "Error: Please provide city name\nUsage: weather <city>"
            
            city = args.strip()
            response = requests.get(f"https://wttr.in/{city}?format=j1")
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                location = data['nearest_area'][0]
                
                return f"""Weather in {location['areaName'][0]['value']}, {location['country'][0]['value']}

Temperature: {current['temp_C']}°C ({current['temp_F']}°F)
Feels Like: {current['FeelsLikeC']}°C ({current['FeelsLikeF']}°F)
Condition: {current['weatherDesc'][0]['value']}
Humidity: {current['humidity']}%
Wind: {current['windspeedKmph']} km/h
Visibility: {current['visibility']} km
Pressure: {current['pressure']} mb

Last Updated: {current['observation_time']}"""
            else:
                return f"Error: Could not fetch weather for '{city}'"
        
        elif command == "forecast":
            if not args:
                return "Error: Please provide city name\nUsage: forecast <city>"
            
            city = args.strip()
            response = requests.get(f"https://wttr.in/{city}?format=j1")
            
            if response.status_code == 200:
                data = response.json()
                location = data['nearest_area'][0]
                forecast = data['weather']
                
                result = f"5-Day Forecast for {location['areaName'][0]['value']}, {location['country'][0]['value']}\n\n"
                
                for day in forecast[:5]:
                    result += f"{day['date']}:\n"
                    result += f"  Max: {day['maxtempC']}°C, Min: {day['mintempC']}°C\n"
                    result += f"  Condition: {day['hourly'][4]['weatherDesc'][0]['value']}\n"
                    result += f"  Rain chance: {day['hourly'][4]['chanceofrain']}%\n\n"
                
                return result
            else:
                return f"Error: Could not fetch forecast for '{city}'"
        
        elif command == "ip":
            response = requests.get("https://ipapi.co/json/")
            
            if response.status_code == 200:
                data = response.json()
                return f"""Your IP Information:

IP Address: {data.get('ip', 'Unknown')}
Location: {data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}, {data.get('country_name', 'Unknown')}
Coordinates: {data.get('latitude', 'Unknown')}, {data.get('longitude', 'Unknown')}
Timezone: {data.get('timezone', 'Unknown')}
ISP: {data.get('org', 'Unknown')}
Postal: {data.get('postal', 'Unknown')}"""
            else:
                return "Error fetching IP information"
        
        elif command == "time":
            if not args:
                return "Error: Please provide city name\nUsage: time <city>"
            
            city = args.strip()
            
            # First get timezone
            response = requests.get(f"https://worldtimeapi.org/api/timezone")
            if response.status_code != 200:
                return "Error fetching timezone list"
            
            timezones = response.json()
            
            # Try to find matching timezone
            matching = [tz for tz in timezones if city.lower() in tz.lower()]
            
            if matching:
                timezone = matching[0]
                time_response = requests.get(f"https://worldtimeapi.org/api/timezone/{timezone}")
                
                if time_response.status_code == 200:
                    time_data = time_response.json()
                    return f"""Current Time in {timezone}:

Date & Time: {time_data['datetime']}
Timezone: {time_data['timezone']}
Abbreviation: {time_data['abbreviation']}
UTC Offset: {time_data['utc_offset']}
Day of Week: {time_data['day_of_week']}
Day of Year: {time_data['day_of_year']}
Week Number: {time_data['week_number']}"""
                else:
                    return "Error fetching time information"
            else:
                return f"Could not find timezone for '{city}'. Try a major city name."
        
        elif command == "timezone":
            if not args:
                return "Error: Please provide city or timezone\nUsage: timezone <city>"
            
            zone = args.strip().replace(" ", "_")
            response = requests.get(f"https://worldtimeapi.org/api/timezone/{zone}")
            
            if response.status_code == 200:
                data = response.json()
                return f"""Timezone Information:

Timezone: {data['timezone']}
Abbreviation: {data['abbreviation']}
UTC Offset: {data['utc_offset']}
Current Time: {data['datetime']}
Is DST: {data['dst']}"""
            else:
                return f"Could not find timezone '{zone}'. Use format like: America/New_York"
        
        else:
            return f"Unknown command: {command}\n\nRun without arguments to see available commands"
    
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
