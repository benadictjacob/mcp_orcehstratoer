"""
CoinGecko MCP Module
Provides cryptocurrency data using the CoinGecko API (no auth required)
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "https://api.coingecko.com/api/v3"

def format_price(price: float) -> str:
    """Format price with appropriate decimal places"""
    if price < 0.01:
        return f"${price:.6f}"
    elif price < 1:
        return f"${price:.4f}"
    else:
        return f"${price:,.2f}"

def format_number(num: float) -> str:
    """Format large numbers with abbreviations"""
    if num >= 1_000_000_000_000:
        return f"${num/1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    else:
        return f"${num:,.0f}"

def get_price(coin_ids: str, currencies: str = "usd") -> Dict[str, Any]:
    """
    Get current price of cryptocurrencies
    
    Args:
        coin_ids: Comma-separated coin IDs (e.g., "bitcoin,ethereum")
        currencies: Comma-separated currencies (default: "usd")
    
    Example: get_price("bitcoin,ethereum,cardano")
    """
    try:
        url = f"{BASE_URL}/simple/price"
        params = {
            "ids": coin_ids,
            "vs_currencies": currencies,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Format the output nicely
        result = []
        for coin_id, coin_data in data.items():
            price = coin_data.get('usd', 0)
            change_24h = coin_data.get('usd_24h_change', 0)
            market_cap = coin_data.get('usd_market_cap', 0)
            volume_24h = coin_data.get('usd_24h_vol', 0)
            
            change_symbol = "[UP]" if change_24h >= 0 else "[DOWN]"
            
            result.append(
                f"**{coin_id.upper()}**\n"
                f"  Price: {format_price(price)}\n"
                f"  24h Change: {change_symbol} {change_24h:+.2f}%\n"
                f"  Market Cap: {format_number(market_cap)}\n"
                f"  24h Volume: {format_number(volume_24h)}\n"
            )
        
        return {
            "success": True,
            "data": "\n".join(result),
            "raw_data": data
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

def search_coins(query: str) -> Dict[str, Any]:
    """
    Search for cryptocurrencies by name or symbol
    
    Args:
        query: Search query (e.g., "bitcoin" or "btc")
    
    Example: search_coins("cardano")
    """
    try:
        url = f"{BASE_URL}/search"
        params = {"query": query}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        coins = data.get("coins", [])[:10]  # Limit to top 10 results
        
        if not coins:
            return {
                "success": True,
                "data": f"No cryptocurrencies found for '{query}'"
            }
        
        result = [f"Found {len(coins)} cryptocurrencies matching '{query}':\n"]
        for coin in coins:
            result.append(
                f"* **{coin['name']}** ({coin['symbol'].upper()})\n"
                f"  ID: {coin['id']}\n"
                f"  Market Rank: #{coin.get('market_cap_rank', 'N/A')}\n"
            )
        
        return {
            "success": True,
            "data": "\n".join(result),
            "coin_ids": [coin['id'] for coin in coins]
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

def get_coin_details(coin_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific cryptocurrency
    
    Args:
        coin_id: CoinGecko coin ID (e.g., "bitcoin")
    
    Example: get_coin_details("ethereum")
    """
    try:
        url = f"{BASE_URL}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "false"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant information
        name = data.get('name', 'N/A')
        symbol = data.get('symbol', 'N/A').upper()
        market_data = data.get('market_data', {})
        
        current_price = market_data.get('current_price', {}).get('usd', 0)
        market_cap = market_data.get('market_cap', {}).get('usd', 0)
        market_cap_rank = market_data.get('market_cap_rank', 'N/A')
        total_volume = market_data.get('total_volume', {}).get('usd', 0)
        
        price_change_24h = market_data.get('price_change_percentage_24h', 0)
        price_change_7d = market_data.get('price_change_percentage_7d', 0)
        price_change_30d = market_data.get('price_change_percentage_30d', 0)
        
        ath = market_data.get('ath', {}).get('usd', 0)
        atl = market_data.get('atl', {}).get('usd', 0)
        
        circulating_supply = market_data.get('circulating_supply', 0)
        total_supply = market_data.get('total_supply', 0)
        
        result = [
            f"**{name} ({symbol})**",
            f"Rank: #{market_cap_rank}",
            "",
            f"[PRICE INFORMATION]",
            f"  Current Price: {format_price(current_price)}",
            f"  24h Change: {price_change_24h:+.2f}%",
            f"  7d Change: {price_change_7d:+.2f}%",
            f"  30d Change: {price_change_30d:+.2f}%",
            "",
            f"[MARKET DATA]",
            f"  Market Cap: {format_number(market_cap)}",
            f"  24h Volume: {format_number(total_volume)}",
            f"  All-Time High: {format_price(ath)}",
            f"  All-Time Low: {format_price(atl)}",
            "",
            f"[SUPPLY]",
            f"  Circulating: {circulating_supply:,.0f} {symbol}",
            f"  Total: {total_supply:,.0f} {symbol}" if total_supply else "  Total: Unlimited"
        ]
        
        return {
            "success": True,
            "data": "\n".join(result),
            "raw_data": data
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

def get_trending() -> Dict[str, Any]:
    """
    Get trending cryptocurrencies
    
    Example: get_trending()
    """
    try:
        url = f"{BASE_URL}/search/trending"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        coins = data.get("coins", [])[:10]
        
        result = ["[TRENDING CRYPTOCURRENCIES]\n"]
        for idx, item in enumerate(coins, 1):
            coin = item.get('item', {})
            result.append(
                f"{idx}. **{coin['name']}** ({coin['symbol']})\n"
                f"   Rank: #{coin.get('market_cap_rank', 'N/A')}\n"
                f"   Price: {format_price(coin.get('price_btc', 0))} BTC\n"
            )
        
        return {
            "success": True,
            "data": "\n".join(result)
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

def get_global_data() -> Dict[str, Any]:
    """
    Get global cryptocurrency market data
    
    Example: get_global_data()
    """
    try:
        url = f"{BASE_URL}/global"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get('data', {})
        
        total_market_cap = data.get('total_market_cap', {}).get('usd', 0)
        total_volume = data.get('total_volume', {}).get('usd', 0)
        btc_dominance = data.get('market_cap_percentage', {}).get('btc', 0)
        eth_dominance = data.get('market_cap_percentage', {}).get('eth', 0)
        active_cryptos = data.get('active_cryptocurrencies', 0)
        markets = data.get('markets', 0)
        
        result = [
            "[GLOBAL CRYPTOCURRENCY MARKET]",
            "",
            f"Total Market Cap: {format_number(total_market_cap)}",
            f"24h Volume: {format_number(total_volume)}",
            f"Active Cryptocurrencies: {active_cryptos:,}",
            f"Markets: {markets:,}",
            "",
            f"**Market Dominance**",
            f"  Bitcoin: {btc_dominance:.2f}%",
            f"  Ethereum: {eth_dominance:.2f}%"
        ]
        
        return {
            "success": True,
            "data": "\n".join(result)
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

def run(input_text: str) -> str:
    """
    Main entry point for CoinGecko MCP
    
    Commands:
        price <coin_ids>       - Get current prices (e.g., "price bitcoin,ethereum")
        search <query>         - Search for cryptocurrencies
        details <coin_id>      - Get detailed coin information
        trending               - Get trending cryptocurrencies
        global                 - Get global market data
        help                   - Show available commands
    """
    parts = input_text.strip().split(maxsplit=1)
    command = parts[0].lower() if parts else "help"
    args = parts[1] if len(parts) > 1 else ""
    
    if command == "price":
        if not args:
            return "[ERROR] Please provide coin IDs. Example: price bitcoin,ethereum"
        result = get_price(args)
        
    elif command == "search":
        if not args:
            return "[ERROR] Please provide a search query. Example: search cardano"
        result = search_coins(args)
        
    elif command == "details":
        if not args:
            return "[ERROR] Please provide a coin ID. Example: details bitcoin"
        result = get_coin_details(args)
        
    elif command == "trending":
        result = get_trending()
        
    elif command == "global":
        result = get_global_data()
        
    elif command == "help":
        return """
[COINGECKO MCP - CRYPTOCURRENCY DATA]

**Available Commands:**

* price <coin_ids> - Get current prices
  Example: price bitcoin,ethereum,cardano

* search <query> - Search for cryptocurrencies
  Example: search solana

* details <coin_id> - Get detailed information
  Example: details ethereum

* trending - Get trending cryptocurrencies

* global - Get global market data

* help - Show this help message

**Note:** All data is fetched from CoinGecko API (no authentication required)
Rate limit: 10-15 calls per minute
"""
    else:
        return f"[ERROR] Unknown command: {command}. Use 'help' to see available commands."
    
    if result.get("success"):
        return result.get("data", "No data available")
    else:
        return f"[ERROR] {result.get('error', 'Unknown error occurred')}"
