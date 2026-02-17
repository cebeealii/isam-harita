import pandas as pd
import os
import glob

# Set display options to show all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

files = glob.glob("/Users/alicebe/Downloads/isam_hazirlik/*.xls")

for f in files:
    print(f"\n--- Inspetores: {os.path.basename(f)} ---")
    try:
        # Try reading with default engine first, then openpyxl or xlrd if needed
        df = pd.read_excel(f, nrows=5) 
        print(df.head())
        print("\nColumns:", df.columns.tolist())
    except Exception as e:
        print(f"Error reading {os.path.basename(f)}: {e}")
