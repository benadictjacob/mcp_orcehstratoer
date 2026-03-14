import requests
import json

def run(input_text: str) -> str:
    """
    Weather Information (using wttr.in - no API key required!)
    
    Commands:
    - weather <city> : Get current weather for a city
    - forecast <city> : Get 3-day forecast
    - moon : Get moon phase information
    """
    
    parts = input_text.strip().split(maxsplit=1)
    
    if not parts:
        return """Weather Information (No API Key Required!)

Available commands:
- weather <city> : Current weather (e.g., weather London)
- forecast <city> : 3-day forecast (e.g., forecast Paris)
- moon : Current moon phase

Examples:
  weather Tokyo
  forecast New York
  moon"""
    
    command = parts[0].lower()
    location = parts[1] if len(parts) > 1 else ""
    
    try:
        if command == "weather":
            if not location:
                return "Error: Please provide a city name\nUsage: weather <city>"
            
            # Using wttr.in - no API key needed!
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                result = f"""Weather in {location}:
                
Temperature: {current['temp_C']}C / {current['temp_F']}F
Feels Like: {current['FeelsLikeC']}C / {current['FeelsLikeF']}F
Condition: {current['weatherDesc'][0]['value']}
Humidity: {current['humidity']}%
Wind: {current['windspeedKmph']} km/h {current['winddir16Point']}
Pressure: {current['pressure']} mb
Visibility: {current['visibility']} km
UV Index: {current['uvIndex']}"""
                return result
            else:
                return f"Error: Could not fetch weather data\nStatus: {response.status_code}"
        
        elif command == "forecast":
            if not location:
                return "Error: Please provide a city name\nUsage: forecast <city>"
            
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                result = f"3-Day Forecast for {location}:\n\n"
                
                for day in data['weather'][:3]:
                    date = day['date']
                    max_temp = day['maxtempC']
                    min_temp = day['mintempC']
                    desc = day['hourly'][4]['weatherDesc'][0]['value']
                    
                    result += f"{date}:\n"
                    result += f"  High: {max_temp}C, Low: {min_temp}C\n"
                    result += f"  Condition: {desc}\n\n"
                
                return result
            else:
                return f"Error: Could not fetch forecast data\nStatus: {response.status_code}"
        
        elif command == "moon":
            url = "https://wttr.in/Moon?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                result = f"""Moon Information:

Phase: {current['weatherDesc'][0]['value']}
Illumination: {current['humidity']}%"""
                return result
            else:
                return f"Error: Could not fetch moon data\nStatus: {response.status_code}"
        
        else:
            return f"Unknown command: {command}\n\nRun without arguments to see available commands"
    
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
