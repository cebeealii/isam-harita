import pandas as pd
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

DATA_FILES = {
    "Household": "İllere Göre Ortalama Hanehalkı Büyüklüğü.xls",
    "MedianAge": "İllere ve cinsiyete göre ortanca yaş.xls",
    "Dependency": "İllere Göre Yaş Bağımlılık Oranı.xls",
    "Population": "Yıllara Göre İl Nüfusları .xls",
    "Marital": "İl, medeni durum ve cinsiyete göre nüfus-2.xls"
}

def find_header_and_load(path, text_marker="Adana", n_look=20):
    print(f"\n--- Loading {os.path.basename(path)} ---")
    try:
        # Load first n rows without header
        df_raw = pd.read_excel(path, header=None, nrows=n_look)
        
        # 1. Find Data Start (Adana)
        adana_idx = -1
        city_col_idx = -1
        for idx, row in df_raw.iterrows():
            matches = row.astype(str).str.contains(text_marker, case=False, na=False)
            if matches.any():
                adana_idx = idx
                city_col_idx = matches.idxmax()
                print(f"Found Data Start '{text_marker}' at Row {adana_idx}, Col {city_col_idx}")
                break
        
        if adana_idx == -1:
            print(f"Could not find marker '{text_marker}'")
            return None

        # 2. Find Header (Provinces/Il) BEFORE Adana
        header_idx = -1
        for idx in range(adana_idx - 1, -1, -1):
            row_vals = df_raw.iloc[idx].astype(str).values
            # Check for "Il" or "Provinces" or "City"
            # Note: "İl" might be encoded weirdly, so check for "Provinces" or casing
            if any("province" in x.lower() for x in row_vals) or any("il" == x.lower().strip() for x in row_vals) or any("il\n" in x.lower() for x in row_vals):
                header_idx = idx
                print(f"Found Header at Row {header_idx}")
                break
        
        if header_idx == -1:
            print("Could not find explicit header row. Guessing Adana - 1")
            header_idx = adana_idx - 1

        # Reload with correct header
        df = pd.read_excel(path, header=header_idx)
        
        # Rename City Column
        # verify city_col_idx matches
        # The column index in df should match city_col_idx
        # But df columns might be named 'Provinces' etc.
        # Let's map the raw col index to the new df column name.
        col_name_at_idx = df.columns[city_col_idx]
        print(f"Renaming column '{col_name_at_idx}' to 'City'")
        df.rename(columns={col_name_at_idx: 'City'}, inplace=True)
        
        # Clean City Column
        # Filter: Keep rows where City column is NOT null and does not look like header/total
        # Actually, just slicing from Adana downwards is safer if we know Adana index relative to header.
        # New Adana index in df = adana_idx - header_idx - 1
        # Example: Adana=4, Header=1. Skip 2 rows (2,3). Data starts at new index 2?
        # Let's just filter by "City" value being valid.
        
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

def clean_city_col(df):
    """Refreshes the City column and drops invalid rows"""
    if 'City' not in df.columns:
        return df
    # Drop rows where City is nan
    df = df.dropna(subset=['City'])
    # Convert to string
    df['City'] = df['City'].astype(str).str.strip()
    # Remove rows that are numeric (Years) or 'Total'
    mask_numeric = df['City'].str.match(r'^\d+$') # Pure numbers
    mask_total = df['City'].str.contains("Total|Toplam|Turkey|Türkiye|Provinces|Year", case=False)
    
    df = df[~mask_numeric & ~mask_total]
    return df

def process():
    merged = None
    
    # helper to find col by string
    def find_col(df, keywords):
        for col in df.columns:
            c_str = str(col).lower()
            if any(k.lower() in c_str for k in keywords):
                return col
        return None

    # 1. Household Size
    # Expected: City, Years...
    df_hh = find_header_and_load(DATA_FILES["Household"], "Adana")
    if df_hh is not None:
        df_hh = clean_city_col(df_hh)
        # Find 2023 or 2024
        col_2023 = find_col(df_hh, ["2023"]) or find_col(df_hh, ["2022"]) or df_hh.columns[-1]
        print(f"Selected Household Col: {col_2023}")
        df_hh = df_hh[['City', col_2023]].copy()
        df_hh.columns = ['City', 'Avg_Household_Size']
        df_hh['Avg_Household_Size'] = pd.to_numeric(df_hh['Avg_Household_Size'], errors='coerce')
        merged = df_hh

    # 2. Median Age
    # Expected: City, Total(2023)...
    df_med = find_header_and_load(DATA_FILES["MedianAge"], "Adana")
    if df_med is not None:
        df_med = clean_city_col(df_med)
        # Columns might get renamed to 2024 due to header row values.
        # Snippet showed: ['City', 2024, ...]
        # Valid column is likely index 1 (Total) if header worked.
        # Let's check if 'Male' or 'Female' is in names to avoid them.
        # Actually, let's just pick the first numeric column after City?
        # Or look for "Total" if it exists in name.
        # But header row 2 had "2024" in col 1.
        # So "2024" is the column name for Total.
        col_total = find_col(df_med, ["Total", "Toplam"]) 
        if not col_total:
             # If headers are just years like 2024, pick 2024.
             col_total = find_col(df_med, ["2024"]) or find_col(df_med, ["2023"]) or df_med.columns[1]
             
        print(f"Selected Median Age Col: {col_total}")
        df_med = df_med[['City', col_total]].copy()
        df_med.columns = ['City', 'Median_Age']
        df_med['Median_Age'] = pd.to_numeric(df_med['Median_Age'], errors='coerce')
        
        if merged is not None:
            merged = pd.merge(merged, df_med, on='City', how='outer')

    # 3. Dependency Ratio
    # Expected: City(1), Dependency(7)
    df_dep = find_header_and_load(DATA_FILES["Dependency"], "Adana")
    if df_dep is not None:
        df_dep = clean_city_col(df_dep)
        
        # Strategy: Keep last entry for each city (closest to present)
        print("Dependency: Keeping last entry per city")
        df_dep = df_dep.drop_duplicates(subset=['City'], keep='last')

        # Look for "Total age dependency"
        col_dep = find_col(df_dep, ["Total age dependency", "Toplam yaş bağımlılık"])
        if not col_dep:
             # Fallback index 7 if we trust structure
             if len(df_dep.columns) > 7:
                 col_dep = df_dep.columns[7]
        
        print(f"Selected Dependency Col: {col_dep}")
        if col_dep:
            # Check City column duplicate? 
            # find_header_and_load renamed one column to City.
            df_dep = df_dep[['City', col_dep]].copy()
            df_dep.columns = ['City', 'Dependency_Ratio']
            df_dep['Dependency_Ratio'] = pd.to_numeric(df_dep['Dependency_Ratio'], errors='coerce')
            if merged is not None:
                merged = pd.merge(merged, df_dep, on='City', how='outer')

    # 4. Population
    df_pop = find_header_and_load(DATA_FILES["Population"], "Adana")
    if df_pop is not None:
        df_pop = clean_city_col(df_pop)
        col_pop = find_col(df_pop, ["2023"]) or find_col(df_pop, ["2024"]) or df_pop.columns[-1]
        print(f"Selected Population Col: {col_pop}")
        df_pop = df_pop[['City', col_pop]].copy()
        df_pop.columns = ['City', 'Population']
        df_pop['Population'] = pd.to_numeric(df_pop['Population'], errors='coerce')
        if merged is not None:
            merged = pd.merge(merged, df_pop, on='City', how='outer')

    # 5. Marital Status
    # Header row 3: ['Yıl', 'City', 'Total', 'Un3', 'Un4', 'Un5', 'Never Married', ...]
    df_mar = find_header_and_load(DATA_FILES["Marital"], "Adana")
    if df_mar is not None:
        df_mar = clean_city_col(df_mar)
        
        # Strategy: Keep last entry per city
        print("Marital: Keeping last entry per city")
        df_mar = df_mar.drop_duplicates(subset=['City'], keep='last')
        
        # Identify columns
        c_total = find_col(df_mar, ["Toplam", "Total"])
        c_single = find_col(df_mar, ["Never married", "Hiç evlenmedi"])
        # Fix Married: Must match 'Married' or 'Evli' but NOT 'Never'
        c_married = None
        for col in df_mar.columns:
            c_s = str(col).lower()
            if ("married" in c_s or "evli" in c_s) and "never" not in c_s and "hiç" not in c_s:
                c_married = col
                break
        
        c_divorced = find_col(df_mar, ["Divorced", "Boşandı"])
        
        print(f"Marital Cols Found: Total={c_total}, Single={c_single}, Married={c_married}, Divorced={c_divorced}")
        
        if c_total and c_single and c_married and c_divorced:
             cols_to_use = ['City', c_total, c_single, c_married, c_divorced]
             # Ensure cols exist
             cols_to_use = [c for c in cols_to_use if c in df_mar.columns]
             df_mar = df_mar[cols_to_use].copy()
             
             # Rename (careful with order or map)
             # simpler to map by name
             mapper = {c_total: 'Marital_Total', c_single: 'Single', c_married: 'Married', c_divorced: 'Divorced'}
             df_mar.rename(columns=mapper, inplace=True)
             
             # numeric
             for c in ['Marital_Total', 'Single', 'Married', 'Divorced']:
                 if c in df_mar.columns:
                    df_mar[c] = pd.to_numeric(df_mar[c], errors='coerce')
             
             if 'Marital_Total' in df_mar.columns:
                 if 'Single' in df_mar.columns: df_mar['Pct_Single'] = df_mar['Single'] / df_mar['Marital_Total']
                 if 'Married' in df_mar.columns: df_mar['Pct_Married'] = df_mar['Married'] / df_mar['Marital_Total']
                 if 'Divorced' in df_mar.columns: df_mar['Pct_Divorced'] = df_mar['Divorced'] / df_mar['Marital_Total']
                 
                 cols_out = ['City'] + [c for c in ['Pct_Single', 'Pct_Married', 'Pct_Divorced'] if c in df_mar.columns]
                 if merged is not None:
                    merged = pd.merge(merged, df_mar[cols_out], on='City', how='outer')

    # Final Cleanup
    if merged is not None:
        merged = clean_city_col(merged)
        print("\nFinal Data Sample:")
        print(merged.head(10))
        merged.to_csv("city_demographics_final.csv", index=False)


if __name__ == "__main__":
    process()
