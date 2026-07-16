# Sales Report Generator

This script reads a CSV file containing sales data, processes it to handle missing values and generates a summary report of total revenue per product line.

## How to Run

1. Make sure `sales_data.csv` is in the same directory as `main.py`.
2. Run the script using Python:
   ```bash
   python main.py
   ```

## CSV Format

The `sales_data.csv` file should have the following columns:
- `Date` (e.g., YYYY-MM-DD)
- `Product Line`
- `Revenue` (numeric)

Missing values for 'Revenue' will be treated as 0.0.
Missing values for 'Product Line' will be categorized as 'Unknown'.
