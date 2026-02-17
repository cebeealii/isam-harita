import pandas as pd
import os
import glob

# Setup output dir
os.makedirs("data_validated", exist_ok=True)

# File match
files = glob.glob("*Hanehalkı*.xls")
if not files:
    print("Error: File not found")
    exit()
filename = files[0]
print(f"Processing: {filename}")

# Load raw with specific header row (Row 2, index=2)
# Based on inspection: 
# Row 0: Title
# Row 1: English Title
# Row 2: Headers (İl-Provinces, 2008, 2009...)
df = pd.read_excel(filename, header=2)

# Rename City Column
# The first column name is likely 'İl-Provinces' or similar. 
# Let's normalize it to 'City'
df.rename(columns={df.columns[0]: 'City'}, inplace=True)

# Filter Rows
# We only want rows where 'City' is a valid string and NOT 'Toplam-Total' or 'Türkiye-Turkey'
# And not NaN
df = df.dropna(subset=['City'])
df = df[~df['City'].astype(str).str.contains("Toplam", case=False)]
df = df[~df['City'].astype(str).str.contains("Turkey", case=False)]

# Select only necessary columns: City + 2023 (or latest available)
# Based on inspection, columns are integers 2008..2025. 
# We want 2023 generally, but let's grab 2023, 2024 if exist.
target_cols = ['City']
for year in [2023, 2024, 2025]:
    if year in df.columns:
        target_cols.append(year)
    elif str(year) in df.columns: # unlikely if read as int
        target_cols.append(str(year))

print(f"Extracting columns: {target_cols}")
df_final = df[target_cols].copy()

# Clean City Names (strip, title case)
df_final['City'] = df_final['City'].astype(str).str.strip().str.title()

# Save
output_path = "data_validated/household_size_clean.csv"
df_final.to_csv(output_path, index=False)
print(f"Saved validated data to {output_path}")
print(df_final.head())
