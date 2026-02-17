import pandas as pd
import os

pd.set_option('display.max_columns', None)

files = [f for f in os.listdir('.') if f.endswith('.xls')]
files.sort()

for f in files:
    print(f"--- Processing: {f} ---")
    try:
        # Try reading as excel
        df = pd.read_excel(f, nrows=5)
        print(df.head())
        print("Columns:", df.columns.tolist())
    except Exception as e:
        print(f"Failed to read with read_excel: {e}")
        try:
            # Fallback for HTML content saved as .xls
            dfs = pd.read_html(f)
            if dfs:
                print("Read using read_html")
                print(dfs[0].head())
        except Exception as e2:
            print(f"Failed to read with read_html: {e2}")
    print("\n")
