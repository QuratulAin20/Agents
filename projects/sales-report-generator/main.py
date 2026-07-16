import csv
from datetime import datetime

def generate_sales_report(file_path):
    product_revenue = {}
    
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Handle missing Product Line
            product_line = row.get('Product Line', '').strip()
            if not product_line:
                product_line = 'Unknown'

            # Handle missing and invalid Revenue
            revenue_str = row.get('Revenue', '').strip()
            try:
                revenue = float(revenue_str)
            except (ValueError, TypeError):
                revenue = 0.0  # Treat missing or invalid revenue as 0

            # Aggregate revenue per product line
            product_revenue[product_line] = product_revenue.get(product_line, 0.0) + revenue
            
            # Date formatting (not directly used for this report's output, but good to parse)
            date_str = row.get('Date')
            if date_str:
                try:
                    # Example of parsing, can be formatted later if needed
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    pass # Handle invalid date format if necessary
    
    print("Sales Summary Report:")
    print("---------------------")
    for product, total_revenue in product_revenue.items():
        print(f"{product}: ${total_revenue:.2f}")

if __name__ == "__main__":
    generate_sales_report('sales_data.csv')
