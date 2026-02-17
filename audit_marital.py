import pandas as pd

# Load validated data
df = pd.read_csv("data_validated/marital_status_clean.csv")

# Ensure numeric
cols = ['Marital_Total_Pop', 'Never_Married', 'Married', 'Divorced', 'Widowed']
for c in cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# Metric 1: % of Total 15+ Population (Current)
df['Rate_All_Adults'] = df['Divorced'] / df['Marital_Total_Pop']

# Metric 2: % of Ever-Married Population (Excludes Single)
df['Ever_Married_Pop'] = df['Married'] + df['Divorced'] + df['Widowed']
df['Rate_Ever_Married'] = df['Divorced'] / df['Ever_Married_Pop']

# Sort and Compare
print("\n--- COMPARISON OF DIVORCE METRICS (Top 5 Cities) ---")
top_cities = df.sort_values('Rate_All_Adults', ascending=False).head(5)
print(top_cities[['City', 'Divorced', 'Marital_Total_Pop', 'Rate_All_Adults', 'Rate_Ever_Married']].to_string(index=False))

print("\n--- COMPARISON OF DIVORCE METRICS (Adana) ---")
adana = df[df['City'] == 'Adana']
print(adana[['City', 'Divorced', 'Marital_Total_Pop', 'Rate_All_Adults', 'Rate_Ever_Married']].to_string(index=False))

print("\n--- AVERAGES ---")
print(f"Avg Rate (All Adults): {df['Rate_All_Adults'].mean():.4f}")
print(f"Avg Rate (Ever Married): {df['Rate_Ever_Married'].mean():.4f}")

