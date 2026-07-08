# Sales Report Generator

This project provides a Python command-line script to process sales data from a CSV file. It handles missing values, formats date strings, and generates a summary report showing total revenue per product line.

## Important Note on Dependencies:

In a real-world scenario, an expert Python developer would typically use the `pandas` library for robust and efficient data manipulation with CSV files. However, to ensure compatibility with the current sandbox environment (which does not allow external library installations), this script has been implemented using only Python's built-in `csv` module and `datetime` for core functionality.

## Files

- `sales_data.csv`: A mock CSV file containing sales data.
- `main.py`: The Python script that performs the data processing and report generation.
- `README.md`: This README file.

## How to Run

1.  Ensure you have Python installed.
2.  Place your sales data CSV file (e.g., `sales_data.csv`) in the same directory as `main.py`.
3.  Run the script from your terminal:
    ```bash
    python main.py
    ```

## CSV File Format

The `sales_data.csv` file should have the following columns:

-   `Date`: The date of the sale (various formats are handled).
-   `Product Line`: The category of the product.
-   `Revenue`: The revenue generated from the sale.

## Example `sales_data.csv`

```csv
Date,Product Line,Revenue
2023-01-01,Electronics,1200
2023/01/02,Clothing,500
2023-01-03,Electronics,null
01-04-2023,Books,300
2023-01-05,,750
2023-01-06,Clothing,150
2023-01-07,Electronics,2000
2023-01-08,Books,null
```

## Output

The script will print the original data, the processed data, and finally, a summary report showing the total revenue for each product line.
