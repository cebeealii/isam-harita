import pandas as pd
import glob
import os

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# 1. Find File
files = glob.glob("*medeni*.xls")
if not files:
    print("No marital file found.")
    exit()
f = files[0]
print(f"Reading: {f}")

# 2. Read Raw
df = pd.read_excel(f)

# 3. Find Rows for specific cities
cities = ['Adana', 'İstanbul', 'İzmir', 'Ankara']
target_rows = []

# Iterate to find the city rows (fuzzy match or direct)
# The structure is complex, so let's look for the City Name in the relevant column (usually 0 or 1)
# Based on previous inspections, data starts after headers.

# Let's verify the columns first
print("Columns:", df.columns.tolist())
print(df.head(10))

# Attempt to find city rows
print("Searching for cities...")
for i, row in df.iterrows():
    # Convert entire row to string to search
    row_str = " ".join(row.astype(str).values).lower()
    
    for city in cities:
        if city.lower() in row_str:
             # Check if it's the main entry (Col 1 is usually the city name)
             # Row 5 had Adana in 'Unnamed: 1'
             if str(row['Unnamed: 1']).strip() == city or str(row['Unnamed: 1']).strip() == city.lower(): 
                 print(f"\n--- Found {city} at index {i} ---")
                 # Print relevant cols
                 # Col 2: Total, Col 9: Married, Col 13: Divorced
                 try:
                     total = row['Unnamed: 2']
                     married = row['Unnamed: 9']
                     divorced = row['Unnamed: 13']
                     print(f"Total (15+): {total}")
                     print(f"Married: {married}")
                     print(f"Divorced: {divorced}")
                     if isinstance(divorced, (int, float)) and isinstance(total, (int, float)):
                         print(f"Divorced/Total: {divorced/total:.2%}")
                     if isinstance(divorced, (int, float)) and isinstance(married, (int, float)):
                         print(f"Divorced/Married: {divorced/married:.2%}")
                 except Exception as e:
                     print(f"Error parse: {e}")
                 print("-" * 20)
