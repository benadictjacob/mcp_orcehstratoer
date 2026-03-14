"""
REST Countries API MCP Integration
Provides country information without authentication
"""

import requests
from typing import Dict, Any

BASE_URL = "https://restcountries.com/v3.1"

def format_country_info(country: Dict[str, Any]) -> str:
    """Format country data into readable text"""
    name = country.get('name', {}).get('common', 'Unknown')
    official = country.get('name', {}).get('official', '')
    
    # Capital
    capitals = country.get('capital', [])
    capital = capitals[0] if capitals else 'N/A'
    
    # Population
    population = country.get('population', 0)
    pop_formatted = f"{population:,}"
    
    # Region and subregion
    region = country.get('region', 'N/A')
    subregion = country.get('subregion', 'N/A')
    
    # Languages
    languages = country.get('languages', {})
    lang_list = ', '.join(languages.values()) if languages else 'N/A'
    
    # Currencies
    currencies = country.get('currencies', {})
    curr_list = []
    for code, info in currencies.items():
        curr_list.append(f"{info.get('name', code)} ({code})")
    currency_str = ', '.join(curr_list) if curr_list else 'N/A'
    
    # Area
    area = country.get('area', 0)
    area_formatted = f"{area:,.0f} km2" if area else 'N/A'
    
    # Timezones
    timezones = country.get('timezones', [])
    tz_str = ', '.join(timezones[:3]) if timezones else 'N/A'
    if len(timezones) > 3:
        tz_str += f" (+{len(timezones)-3} more)"
    
    # Borders
    borders = country.get('borders', [])
    border_count = len(borders)
    
    output = f"""
**{name.upper()}**
Official Name: {official}
Capital: {capital}
Region: {region} ({subregion})
Population: {pop_formatted}
Area: {area_formatted}
Languages: {lang_list}
Currencies: {currency_str}
Timezones: {tz_str}
Bordering Countries: {border_count}
"""
    
    return output.strip()

def search_by_name(name: str) -> str:
    """Search countries by name"""
    try:
        response = requests.get(f"{BASE_URL}/name/{name}")
        if response.status_code == 404:
            return f"No countries found matching '{name}'"
        response.raise_for_status()
        
        countries = response.json()
        
        if len(countries) == 1:
            return format_country_info(countries[0])
        else:
            # Multiple matches
            result = f"Found {len(countries)} countries matching '{name}':\n\n"
            for country in countries[:5]:  # Limit to 5
                result += format_country_info(country) + "\n" + "="*50 + "\n"
            if len(countries) > 5:
                result += f"\n... and {len(countries)-5} more countries"
            return result
            
    except requests.exceptions.RequestException as e:
        return f"Error fetching country data: {str(e)}"

def search_by_code(code: str) -> str:
    """Search country by ISO code (alpha2 or alpha3)"""
    try:
        response = requests.get(f"{BASE_URL}/alpha/{code}")
        if response.status_code == 404:
            return f"No country found with code '{code}'"
        response.raise_for_status()
        
        country = response.json()
        if isinstance(country, list):
            country = country[0]
            
        return format_country_info(country)
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching country data: {str(e)}"

def search_by_capital(capital: str) -> str:
    """Search countries by capital city"""
    try:
        response = requests.get(f"{BASE_URL}/capital/{capital}")
        if response.status_code == 404:
            return f"No countries found with capital '{capital}'"
        response.raise_for_status()
        
        countries = response.json()
        
        result = f"Found {len(countries)} country/countries with capital matching '{capital}':\n\n"
        for country in countries:
            result += format_country_info(country) + "\n"
            
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching country data: {str(e)}"

def search_by_region(region: str) -> str:
    """Search countries by region (Africa, Americas, Asia, Europe, Oceania)"""
    try:
        response = requests.get(f"{BASE_URL}/region/{region}")
        if response.status_code == 404:
            return f"No countries found in region '{region}'"
        response.raise_for_status()
        
        countries = response.json()
        
        # Sort by population
        countries_sorted = sorted(countries, key=lambda x: x.get('population', 0), reverse=True)
        
        result = f"**{region.upper()} REGION** - {len(countries)} countries\n\n"
        result += "Top 10 by population:\n"
        
        for i, country in enumerate(countries_sorted[:10], 1):
            name = country.get('name', {}).get('common', 'Unknown')
            pop = country.get('population', 0)
            capital = country.get('capital', ['N/A'])[0]
            result += f"{i}. {name} - Pop: {pop:,} - Capital: {capital}\n"
            
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching region data: {str(e)}"

def search_by_language(language: str) -> str:
    """Search countries by language"""
    try:
        response = requests.get(f"{BASE_URL}/lang/{language}")
        if response.status_code == 404:
            return f"No countries found speaking '{language}'"
        response.raise_for_status()
        
        countries = response.json()
        
        result = f"Found {len(countries)} countries where '{language}' is spoken:\n\n"
        for country in countries[:10]:  # Limit to 10
            name = country.get('name', {}).get('common', 'Unknown')
            pop = country.get('population', 0)
            result += f"{name} - Population: {pop:,}\n"
            
        if len(countries) > 10:
            result += f"\n... and {len(countries)-10} more countries"
            
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching language data: {str(e)}"

def search_by_currency(currency: str) -> str:
    """Search countries by currency code (e.g., USD, EUR)"""
    try:
        response = requests.get(f"{BASE_URL}/currency/{currency}")
        if response.status_code == 404:
            return f"No countries found using currency '{currency}'"
        response.raise_for_status()
        
        countries = response.json()
        
        result = f"Found {len(countries)} countries using '{currency}':\n\n"
        for country in countries:
            name = country.get('name', {}).get('common', 'Unknown')
            currencies = country.get('currencies', {})
            curr_info = currencies.get(currency.upper(), {})
            curr_name = curr_info.get('name', currency)
            result += f"{name} - {curr_name}\n"
            
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching currency data: {str(e)}"

def get_all_countries() -> str:
    """Get list of all countries"""
    try:
        response = requests.get(f"{BASE_URL}/all")
        response.raise_for_status()
        
        countries = response.json()
        
        # Sort by population
        countries_sorted = sorted(countries, key=lambda x: x.get('population', 0), reverse=True)
        
        result = f"**ALL COUNTRIES** - Total: {len(countries)}\n\n"
        result += "Top 20 by population:\n"
        
        for i, country in enumerate(countries_sorted[:20], 1):
            name = country.get('name', {}).get('common', 'Unknown')
            pop = country.get('population', 0)
            result += f"{i}. {name} - {pop:,}\n"
            
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching countries data: {str(e)}"

def show_help() -> str:
    """Show available commands"""
    return """
**REST COUNTRIES API - Available Commands:**

- name <country_name> - Search by country name
  Example: name india, name united kingdom

- code <iso_code> - Search by ISO code (2 or 3 letter)
  Example: code IN, code USA, code GBR

- capital <capital_name> - Search by capital city
  Example: capital delhi, capital london

- region <region_name> - List countries in region
  Regions: Africa, Americas, Asia, Europe, Oceania
  Example: region asia

- language <language> - Countries by language
  Example: language spanish, language hindi

- currency <code> - Countries by currency code
  Example: currency USD, currency EUR, currency INR

- all - List all countries (top 20 by population)

- help - Show this help message

All searches are case-insensitive and no authentication required!
"""

def run(input: str = "") -> str:
    """
    Main entry point for countries API
    Commands: name, code, capital, region, language, currency, all, help
    """
    if not input or input.strip().lower() == "help":
        return show_help()
    
    parts = input.strip().split(maxsplit=1)
    command = parts[0].lower()
    
    if len(parts) < 2 and command not in ['all', 'help']:
        return f"Error: '{command}' requires an argument. Use 'help' for usage."
    
    query = parts[1] if len(parts) > 1 else ""
    
    if command == "name":
        return search_by_name(query)
    elif command == "code":
        return search_by_code(query)
    elif command == "capital":
        return search_by_capital(query)
    elif command == "region":
        return search_by_region(query)
    elif command == "language" or command == "lang":
        return search_by_language(query)
    elif command == "currency" or command == "curr":
        return search_by_currency(query)
    elif command == "all":
        return get_all_countries()
    elif command == "help":
        return show_help()
    else:
        return f"Unknown command: '{command}'. Use 'help' for available commands."
