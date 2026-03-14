"""Excel/CSV creator module for generating sample data"""
import json
import os
import csv
from datetime import datetime, timedelta
import random

def run(input_text=""):
    """Create CSV file with dummy data (can be opened in Excel)
    
    Usage: 
    - No input: Creates file in current directory
    - With path: Creates file in specified directory (e.g., C:/Users/YourName/Documents/sales_data.csv)
    """
    try:
        # Determine output path
        if input_text and input_text.strip():
            output_file = input_text.strip()
            # Ensure it has .csv extension
            if not output_file.lower().endswith('.csv'):
                output_file += '.csv'
        else:
            output_file = "sales_data.csv"
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Sample data
        products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Webcam", "USB Cable", "Desk Lamp"]
        categories = ["Electronics", "Accessories", "Peripherals", "Office Supplies"]
        sales_reps = ["John Smith", "Emma Davis", "Michael Brown", "Sarah Wilson", "David Lee"]
        regions = ["North", "South", "East", "West", "Central"]
        
        # Headers
        headers = ["ID", "Date", "Product", "Category", "Quantity", "Unit Price", "Total", "Sales Rep", "Region"]
        
        # Generate data
        data = []
        start_date = datetime(2024, 1, 1)
        
        for i in range(1, 51):
            row_id = i
            date = start_date + timedelta(days=random.randint(0, 365))
            product = random.choice(products)
            category = random.choice(categories)
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(10, 500), 2)
            total = round(quantity * unit_price, 2)
            sales_rep = random.choice(sales_reps)
            region = random.choice(regions)
            
            data.append([row_id, date.strftime("%Y-%m-%d"), product, category, quantity, unit_price, total, sales_rep, region])
        
        # Save as CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        
        return json.dumps({
            "success": True,
            "message": f"CSV file created successfully with 50 rows of dummy sales data!",
            "file": os.path.basename(output_file),
            "location": os.path.abspath(output_file),
            "rows": 50,
            "columns": len(headers),
            "note": "This CSV file can be opened in Excel"
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error creating CSV file: {str(e)}"
        })
