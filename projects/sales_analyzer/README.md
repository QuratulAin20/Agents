# Sales Data Analyzer

This project contains a Python script (`main.py`) that reads sales data from a CSV file, processes it, and generates a summary report.

## Features

- Reads sales data from `sales_data.csv`.
- Handles missing values in numerical columns (fills with 0).
- Handles missing product line values (fills with 'Unknown').
- Converts various date string formats to a consistent datetime object.
- Calculates and reports total revenue per product line.

## How to Run

1. Make sure you have `pandas` installed (`pip install pandas`).
2. Place your `sales_data.csv` file in the same directory as `main.py`.
3. Run the script from your terminal:
   ```bash
   python main.py
   ```

## Expected Output

The script will print a summary report showing the total revenue for each product line, followed by the processed detailed DataFrame.
