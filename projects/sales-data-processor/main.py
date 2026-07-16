import csv
import datetime

def process_sales_data(file_path):
    product_line_revenue = {}

    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Handle missing values for Units Sold and Revenue
                units_sold = int(row.get('Units Sold') or 0)
                revenue = float(row.get('Revenue') or 0.0)

                product_line = row.get('Product Line', 'Unknown')

                # Date formatting (for potential future use, not strictly needed for this summary)
                # try:
                #     # Attempt to parse common date formats
                #     date_str = row.get('Date')
                #     if '-' in date_str:
                #         parsed_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                #     elif '/' in date_str:
                #         parsed_date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
                #     else:
                #         parsed_date = None # Could not parse date
                # except (ValueError, TypeError):
                #     parsed_date = None

                product_line_revenue[product_line] = product_line_revenue.get(product_line, 0.0) + revenue

            except (ValueError, TypeError) as e:
                print(f"Skipping row due to data error: {row} - {e}")
                continue
    return product_line_revenue

def generate_summary_report(product_line_revenue):
    print("Sales Summary Report:")
    print("----------------------")
    for product_line, total_revenue in product_line_revenue.items():
        print(f"{product_line}: ${total_revenue:,.2f}")
    print("----------------------")

if __name__ == "__main__":
    csv_file_path = 'sales_data.csv'
    summary = process_sales_data(csv_file_path)
    generate_summary_report(summary)
