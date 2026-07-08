import csv
from datetime import datetime

def load_data(file_path):
    """Loads sales data from a CSV file using built-in csv module."""
    data = []
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None

def parse_date(date_str):
    """Attempts to parse a date string into YYYY-MM-DD format."""
    formats = [
        "%Y-%m-%d",  # 2023-01-01
        "%Y/%m/%d",  # 2023/01/02
        "%m-%d-%Y",  # 01-04-2023
        "%m/%d/%Y",  # 01/04/2023
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None  # Return None if no format matches

def preprocess_data(data):
    """Handles missing values and formats dates for a list of dicts."""
    processed_data = []
    for row in data:
        # Handle 'Product Line'
        product_line = row.get('Product Line', '').strip()
        if not product_line:
            product_line = 'Unknown'

        # Handle 'Revenue'
        revenue_str = row.get('Revenue', '').strip()
        revenue = 0.0
        if revenue_str and revenue_str.lower() != 'null':
            try:
                revenue = float(revenue_str)
            except ValueError:
                revenue = 0.0 # Default to 0 if conversion fails

        # Handle 'Date'
        date_str = row.get('Date', '').strip()
        formatted_date = parse_date(date_str)
        if not formatted_date:
            # If date cannot be parsed, you might want to log, skip, or use a default
            # For simplicity, we'll keep it as original or None for now, and filter later if needed.
            pass # We will drop rows with unparseable dates in the summary step

        processed_data.append({
            'Date': formatted_date,
            'Product Line': product_line,
            'Revenue': revenue
        })
    # Filter out rows where date couldn't be parsed
    processed_data = [row for row in processed_data if row['Date'] is not None]
    return processed_data

def generate_summary_report(data):
    """Generates a summary report of total revenue per product line."""
    summary = {}
    for row in data:
        product_line = row['Product Line']
        revenue = row['Revenue']
        summary[product_line] = summary.get(product_line, 0.0) + revenue
    
    # Convert to a list of dicts for pretty printing and sorting
    report = [{'Product Line': pl, 'Total Revenue': rev} for pl, rev in summary.items()]
    report.sort(key=lambda x: x['Total Revenue'], reverse=True)
    return report

def main():
    file_path = 'sales_data.csv'
    data = load_data(file_path)

    if data is not None:
        print("Original Data:")
        # Print original data in a readable format
        if data:
            headers = list(data[0].keys())
            print(" | ".join(headers))
            print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
            for row in data:
                print(" | ".join(str(row.get(h, '')) for h in headers))
        else:
            print("No data to display.")

        print("\n" + "="*30 + "\n")
        
        processed_data = preprocess_data(data)
        
        print("Processed Data:")
        if processed_data:
            headers = list(processed_data[0].keys())
            print(" | ".join(headers))
            print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
            for row in processed_data:
                print(" | ".join(str(row.get(h, '')) for h in headers))
        else:
            print("No processed data to display.")
        print("\n" + "="*30 + "\n")
        
        report = generate_summary_report(processed_data)
        
        print("Sales Summary Report (Total Revenue per Product Line):")
        if report:
            # Assuming all report items have the same keys
            headers = list(report[0].keys())
            print(" | ".join(headers))
            print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
            for item in report:
                print(" | ".join(str(item.get(h, '')) for h in headers))
        else:
            print("No summary report to display.")

if __name__ == "__main__":
    main()
