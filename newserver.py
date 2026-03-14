import requests
import gzip

try:
    from mcp.server.fastmcp import FastMCP as Server
except ImportError:
    from mcp.server.fastmcp import Server

server = Server("sap-sales-demo")

# === CONFIGURATION ===
API_KEY = "oI7Xs3UXQVzY6IG0ThAber4hIxuAfbwX"
SANDBOX_URL = "https://sandbox.api.sap.com/s4hanacloud"

@server.tool()
def list_sales_orders(top: int = 5):
    """Fetch top Sales Orders from the SAP S/4HANA Sandbox"""
    try:
        api_url = f"{SANDBOX_URL}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder?$top={top}"
        
        headers = {
            'APIKey': 'oI7Xs3UXQVzY6IG0ThAber4hIxuAfbwX',
            'Accept': 'application/json',
            'User-Agent': 'curl/7.68.0'  # Mimic curl exactly
        }
        
        # Make request without explicit compression headers - let requests handle it
        response = requests.get(api_url, headers=headers)
        
        # Debug info
        print(f"Status: {response.status_code}")
        print(f"Content-Encoding: {response.headers.get('content-encoding', 'none')}")
        print(f"Content-Length: {len(response.content)}")
        print(f"Response text length: {len(response.text)}")
        print(f"First 100 chars: {response.text[:100]}")
        
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        # Format response
        orders = data.get('d', {}).get('results', [])
        simplified_orders = []
        for order in orders:
            simplified_orders.append({
                'SalesOrder': order.get('SalesOrder'),
                'Customer': order.get('SoldToParty'),
                'NetAmount': order.get('TotalNetAmount'),
                'Currency': order.get('TransactionCurrency'),
                'Status': order.get('OverallSDProcessStatus')
            })
        
        return simplified_orders
        
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {str(e)}")
        return f"An error occurred: {str(e)}"

@server.tool()
def get_sales_order_details(order_id: str):
    """Get comprehensive details for a specific Sales Order"""
    try:
        api_url = f"{SANDBOX_URL}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder('{order_id}')"
        headers = {
            'APIKey': API_KEY,
            'Accept': 'application/json',
            'User-Agent': 'curl/7.68.0'
        }
        
        response = requests.get(api_url, headers=headers)
        
        # Debug info
        print(f"Getting details for order {order_id}")
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        response.raise_for_status()
        
        # Parse JSON and return full details
        data = response.json()
        return data.get('d', {})
        
    except Exception as e:
        print(f"Exception getting order details: {type(e).__name__}: {str(e)}")
        return f"An error occurred: {str(e)}"

@server.tool()
def search_orders_by_date(start_date: str, end_date: str, top: int = 10):
    """Search Sales Orders within a date range (dates in format YYYY-MM-DD)"""
    try:
        # Format dates for OData filter (SAP expects datetime format)
        formatted_start = f"{start_date}T00:00:00"
        formatted_end = f"{end_date}T23:59:59"
        
        api_url = f"{SANDBOX_URL}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
        params = {
            '$filter': f"CreationDate ge datetime'{formatted_start}' and CreationDate le datetime'{formatted_end}'",
            '$top': top
        }
        
        headers = {
            'APIKey': API_KEY,
            'Accept': 'application/json',
            'User-Agent': 'curl/7.68.0'
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        
        # Debug info
        print(f"Searching orders from {start_date} to {end_date}")
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        # Format response similar to list_sales_orders
        orders = data.get('d', {}).get('results', [])
        simplified_orders = []
        for order in orders:
            simplified_orders.append({
                'SalesOrder': order.get('SalesOrder'),
                'Customer': order.get('SoldToParty'),
                'NetAmount': order.get('TotalNetAmount'),
                'Currency': order.get('TransactionCurrency'),
                'Status': order.get('OverallSDProcessStatus'),
                'CreationDate': order.get('CreationDate')
            })
        
        return simplified_orders
        
    except Exception as e:
        print(f"Exception searching orders by date: {type(e).__name__}: {str(e)}")
        return f"An error occurred: {str(e)}"

@server.tool()
def get_high_value_orders(min_amount: float = 10000, top: int = 10):
    """Get high-value orders above specified amount using server-side filtering"""
    try:
        # Use server-side filtering instead of client-side
        api_url = "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
        
        headers = {
            'APIKey': 'oI7Xs3UXQVzY6IG0ThAber4hIxuAfbwX',
            'Accept': 'application/json',
            'User-Agent': 'python-requests/2.28.0'
        }
        
        # Use OData filtering on the server side
        params = {
            '$filter': f"TotalNetAmount gt {min_amount}",
            '$top': top,
            '$orderby': 'TotalNetAmount desc'  # Sort by amount descending
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        raw_orders = data.get('d', {}).get('results', [])
        
        # Process the filtered results
        high_value_orders = []
        for order in raw_orders:
            high_value_orders.append({
                'SalesOrder': order.get('SalesOrder'),
                'Customer': order.get('SoldToParty'), 
                'NetAmount': order.get('TotalNetAmount'),
                'Currency': order.get('TransactionCurrency'),
                'Status': order.get('OverallSDProcessStatus'),
                'OrderDate': order.get('SalesOrderDate')
            })
        
        return high_value_orders
        
    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@server.tool()
def get_orders_by_status(status: str = "C", top: int = 10):
    """Get orders by processing status (A=Not processed, B=Partially processed, C=Completed)"""
    try:
        api_url = f"{SANDBOX_URL}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
        params = {
            '$filter': f"OverallSDProcessStatus eq '{status}'",
            '$top': top
        }
        
        headers = {
            'APIKey': API_KEY,
            'Accept': 'application/json',
            'User-Agent': 'curl/7.68.0'
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        
        # Debug info
        print(f"Searching for orders with status: {status}")
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        # Format response similar to other functions
        orders = data.get('d', {}).get('results', [])
        simplified_orders = []
        for order in orders:
            simplified_orders.append({
                'SalesOrder': order.get('SalesOrder'),
                'Customer': order.get('SoldToParty'),
                'NetAmount': order.get('TotalNetAmount'),
                'Currency': order.get('TransactionCurrency'),
                'Status': order.get('OverallSDProcessStatus')
            })
        
        return simplified_orders
        
    except Exception as e:
        print(f"Exception getting orders by status: {type(e).__name__}: {str(e)}")
        return f"An error occurred: {str(e)}"

@server.tool()
def get_customer_orders(customer_id: str, top: int = 10):
    """Get all orders for a specific customer"""
    try:
        api_url = f"{SANDBOX_URL}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
        params = {
            '$filter': f"SoldToParty eq '{customer_id}'",
            '$top': top,
            '$orderby': 'CreationDate desc'
        }
        
        headers = {
            'APIKey': API_KEY,
            'Accept': 'application/json',
            'User-Agent': 'curl/7.68.0'
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        
        # Debug info
        print(f"Getting orders for customer: {customer_id}")
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        # Format response similar to other functions
        orders = data.get('d', {}).get('results', [])
        customer_orders = []
        for order in orders:
            customer_orders.append({
                'SalesOrder': order.get('SalesOrder'),
                'Customer': order.get('SoldToParty'),
                'NetAmount': order.get('TotalNetAmount'),
                'Currency': order.get('TransactionCurrency'),
                'Status': order.get('OverallSDProcessStatus'),
                'CreationDate': order.get('CreationDate')
            })
        
        return customer_orders
        
    except Exception as e:
        print(f"Exception getting customer orders: {type(e).__name__}: {str(e)}")
        return f"An error occurred: {str(e)}"

@server.tool()
def get_top_customers_by_revenue(top: int = 5):
    """Get customers with highest total sales revenue"""
    try:
        # Note: SAP OData services may not support $apply aggregation
        # We'll use a fallback approach by getting all orders and aggregating client-side
        api_url = f"{SANDBOX_URL}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
        
        headers = {
            'APIKey': API_KEY,
            'Accept': 'application/json',
            'User-Agent': 'curl/7.68.0'
        }
        
        # First, try the aggregation approach
        try:
            params = {
                '$apply': f"groupby((SoldToParty), aggregate(TotalNetAmount with sum as TotalRevenue))",
                '$orderby': 'TotalRevenue desc',
                '$top': top
            }
            
            response = requests.get(api_url, headers=headers, params=params)
            
            print(f"Trying aggregation approach")
            print(f"Status: {response.status_code}")
            print(f"URL: {response.url}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('d', {}).get('results', [])
                
                top_customers = []
                for result in results:
                    top_customers.append({
                        'Customer': result.get('SoldToParty'),
                        'TotalRevenue': result.get('TotalRevenue'),
                        'Currency': 'USD'  # Assuming USD as most common
                    })
                
                return top_customers
                
        except Exception as agg_error:
            print(f"Aggregation failed: {agg_error}")
            
        # Fallback: Get all orders and aggregate client-side
        print("Using client-side aggregation fallback")
        params = {
            '$top': 1000  # Get more orders for better aggregation
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        orders = data.get('d', {}).get('results', [])
        
        # Aggregate by customer
        customer_totals = {}
        for order in orders:
            customer = order.get('SoldToParty')
            amount = float(order.get('TotalNetAmount', 0) or 0)
            currency = order.get('TransactionCurrency', 'USD')
            
            if customer:
                if customer not in customer_totals:
                    customer_totals[customer] = {
                        'total': 0,
                        'currency': currency
                    }
                customer_totals[customer]['total'] += amount
        
        # Sort by total revenue and get top customers
        sorted_customers = sorted(
            customer_totals.items(), 
            key=lambda x: x[1]['total'], 
            reverse=True
        )[:top]
        
        top_customers = []
        for customer_id, data in sorted_customers:
            top_customers.append({
                'Customer': customer_id,
                'TotalRevenue': str(data['total']),
                'Currency': data['currency']
            })
        
        return top_customers
        
    except Exception as e:
        print(f"Exception getting top customers by revenue: {type(e).__name__}: {str(e)}")
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    server.run(transport='stdio')