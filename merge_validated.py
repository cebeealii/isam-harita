import pandas as pd
import os

# Load Validated Data
df_house = pd.read_csv("data_validated/household_size_clean.csv")
df_marital = pd.read_csv("data_validated/marital_status_clean.csv")

# Standardize City Names
df_house['City'] = df_house['City'].str.strip().str.title()
df_marital['City'] = df_marital['City'].str.strip().str.title()

# Merge All
# House + Marital
df_final = pd.merge(df_house, df_marital, on='City', how='inner')

# Identify 2023 Household Size column
year_cols = [c for c in df_final.columns if c.startswith('20')]
latest_year = sorted(year_cols)[-1]
print(f"Using Household Size Year: {latest_year}")

# Rename for clarity
df_final.rename(columns={latest_year: 'Avg_Household_Size'}, inplace=True)

# Select features for analysis
# We want: City, Avg_Household_Size, Pct_Divorced, Pct_Never_Married
features = ['City', 'Avg_Household_Size', 'Pct_Divorced', 'Pct_Never_Married', 'Pct_Married']
df_analysis = df_final[features].copy()

# Deduplicate just in case (keep first/latest because 2025 is at top)
df_analysis = df_analysis.drop_duplicates(subset=['City'], keep='first')

# Save
output_path = "city_demographics_validated_final.csv"
df_analysis.to_csv(output_path, index=False)
print(f"Saved merged data to {output_path}")
print(df_analysis.head())
