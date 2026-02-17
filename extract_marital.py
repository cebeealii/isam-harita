import pandas as pd
import glob
import os

# Setup
os.makedirs("data_validated", exist_ok=True)
files = glob.glob("*medeni durum*.xls")
if not files:
    print("Error: Marital file not found")
    exit()
filename = files[0]

# Load Raw
# Header roughly at row 3 (0-based idx)
df = pd.read_excel(filename, header=None)

# Extract specific columns by index based on inspection
# Col 1: City
# Col 2: Total 15+ Population
# Col 6: Never Married (Total)
# Col 10: Married (Total)
# Col 14: Divorced (Total)
# Col 18: Widowed (Total)

# Data starts usually at row 6 (based on previous inspection)
# We will filter for valid cities.

clean_rows = []

# Iterating to find data rows
for idx, row in df.iterrows():
    # Check if Col 1 is a city name (string, not NaN, not 'İl..', not 'Toplam')
    city_val = str(row[1])
    if pd.isna(row[1]) or city_val.strip() in ['nan', 'İl-Provinces', 'Toplam-Total', 'Türkiye-Turkey']:
        continue
    
    # Check if it has numeric data in Col 2 (Population)
    try:
        pop = float(row[2])
    except:
        continue
        
    # Extract
    city_name = city_val.strip()
    total_pop = row[2]
    never_married = row[6]
    married = row[10]
    divorced = row[14]
    widowed = row[18]
    
    clean_rows.append({
        'City': city_name,
        'Marital_Total_Pop': total_pop,
        'Never_Married': never_married,
        'Married': married,
        'Divorced': divorced,
        'Widowed': widowed
    })

df_clean = pd.DataFrame(clean_rows)

# Calculate Percentages
df_clean['Pct_Married'] = df_clean['Married'] / df_clean['Marital_Total_Pop']
df_clean['Pct_Divorced'] = df_clean['Divorced'] / df_clean['Marital_Total_Pop']
df_clean['Pct_Never_Married'] = df_clean['Never_Married'] / df_clean['Marital_Total_Pop']
df_clean['Pct_Widowed'] = df_clean['Widowed'] / df_clean['Marital_Total_Pop']

# New Metric: % of Ever-Married Population
df_clean['Ever_Married_Pop'] = df_clean['Married'] + df_clean['Divorced'] + df_clean['Widowed']
df_clean['Pct_Divorced_Ever_Married'] = df_clean['Divorced'] / df_clean['Ever_Married_Pop']

# Save
output_path = "data_validated/marital_status_clean.csv"
df_clean.to_csv(output_path, index=False)
print(f"Saved {len(df_clean)} rows to {output_path}")
print(df_clean[['City', 'Pct_Divorced', 'Pct_Married']].head())
