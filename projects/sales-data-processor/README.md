# Sales Data Processor

This project provides a command-line script to process sales data from a CSV file. It handles missing values, and generates a summary report showing total revenue per product line.

## Files:
- `sales_data.csv`: Sample CSV file containing sales data.
- `main.py`: The main Python script to process the data.

## Usage:
Run the `main.py` script to process the `sales_data.csv` file and print the summary report.

```bash
python main.py
```

## Features:
- Reads sales data from a CSV file.
- Handles missing 'Units Sold' and 'Revenue' values by treating them as 0.
- Calculates total revenue for each product line.
- Prints a formatted summary report.
