import pandas as pd
import glob
import os

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# fuzzy match because of unicode
files = [f for f in os.listdir('.') if 'ag' in f and 'ml' in f and 'Oran' in f and f.endswith('.xls')]
if not files:
    print("Could not find Dependency Ratio file.")
    # Debug list
    print("Files in dir:", os.listdir('.'))
    exit()

f = files[0]
print(f"Inspecting: {f}")

# Read raw
df = pd.read_excel(f, header=None)
print("\n--- RAW DATA (First 20 Rows) ---")
print(df.head(20))

print("\n--- Checking for 'Adana' ---")
# Find where Adana is
mask = df.apply(lambda x: x.astype(str).str.contains('Adana', case=False, na=False))
rows, cols = mask.values.nonzero()
if len(rows) > 0:
    print(f"Found 'Adana' at Row: {rows[0]}, Col: {cols[0]}")
    print("Row data:")
    print(df.iloc[rows[0]])
else:
    print("Could not find 'Adana'")
