import pandas as pd
import glob
import os

# Setup
os.makedirs("data_validated", exist_ok=True)
# File match with fuzzy logic for unicode
files = [f for f in os.listdir('.') if 'Oran' in f and f.endswith('.xls')]
if not files:
    print("Error: Dependency file not found")
    exit()
filename = files[0]
print(f"Processing: {filename}")

# Load raw
# Based on inspection:
# Adana is at Row 5
# Header is effectively Row 4 (0-based 4? No, Row 4 in Excel is Index 3 in pandas if header=None)
# Let's read with header=None and manually slice to be safe.
df = pd.read_csv(filename, sep='\t') if filename.endswith('.txt') else pd.read_excel(filename, header=None)

# Iterate and extract
clean_rows = []
for idx, row in df.iterrows():
    # Helper to check if row[1] is a city
    val = str(row[1])
    if pd.isna(row[1]) or val.strip() in ['nan', 'İl-Provinces', 'Toplam-Total', 'Türkiye-Turkey']:
        continue
    
    # Check if we have data in Col 7 (Total Dep Ratio)
    try:
        total_dep = float(row[7])
        child_dep = float(row[8])
        elderly_dep = float(row[9])
    except:
        continue
        
    city_name = val.strip()
    
    clean_rows.append({
        'City': city_name,
        'Total_Dependency_Ratio': total_dep,
        'Child_Dependency_Ratio': child_dep,
        'Elderly_Dependency_Ratio': elderly_dep
    })

df_clean = pd.DataFrame(clean_rows)

# Save
output_path = "data_validated/dependency_ratio_clean.csv"
df_clean.to_csv(output_path, index=False)
print(f"Saved {len(df_clean)} rows to {output_path}")
print(df_clean.head())
