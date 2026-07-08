import pandas as pd

def analyze_sales(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Handle missing values
    # Fill numerical columns with 0
    numerical_cols = ['Units Sold', 'Price per Unit', 'Revenue']
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Fill 'Product Line' with 'Unknown' if missing
    if 'Product Line' in df.columns:
        df['Product Line'] = df['Product Line'].fillna('Unknown')

    # Convert Date column to datetime objects
    if 'Date' in df.columns:
        # Try multiple date formats
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=False)
        # Drop rows where date conversion failed
        df.dropna(subset=['Date'], inplace=True)
    else:
        print("Warning: 'Date' column not found in the CSV.")
        return

    # Calculate total revenue per product line
    # If Revenue was missing, it's now 0, so the sum will be correct.
    # If Price per Unit or Units Sold was missing, Revenue might still be NaN if it wasn't pre-calculated.
    # Let's ensure Revenue is correctly calculated if it was missing but Units Sold and Price per Unit exist.
    if 'Revenue' in df.columns and 'Units Sold' in df.columns and 'Price per Unit' in df.columns:
        df['Revenue'] = df.apply(
            lambda row: row['Units Sold'] * row['Price per Unit'] if row['Revenue'] == 0 and row['Units Sold'] > 0 and row['Price per Unit'] > 0 else row['Revenue'],
            axis=1
        )
    else:
        print("Warning: 'Revenue', 'Units Sold', or 'Price per Unit' column(s) not found. Revenue calculation might be incomplete.")

    summary_report = df.groupby('Product Line')['Revenue'].sum().reset_index()
    summary_report.rename(columns={'Revenue': 'Total Revenue'}, inplace=True)

    print("--- Sales Summary Report ---")
    print(summary_report.to_string(index=False))
    print("\n--- Details ---")
    print(df.to_string())

if __name__ == "__main__":
    analyze_sales('sales_data.csv')
