import pandas as pd
import folium
import requests
import json
import os

# Data Paths
CSV_PATH = "data_validated/household_size_clean.csv"
GEOJSON_URLS = [
    "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/turkey.geojson",
    "https://raw.githubusercontent.com/volkansengul/turkey-geojson/master/turkey.json",
    "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json"
]
OUTPUT_HTML = "household_size_map.html"

def normalize_turkish(text):
    if not isinstance(text, str): return str(text)
    mapping = {
        'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 
        'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 
        'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
    }
    text = text.replace("İ", "I").upper()
    for k, v in mapping.items():
        if k in text: text = text.replace(k, v)
    normalization = {'I': 'I', 'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for k, v in normalization.items():
        text = text.replace(k, v)
    return text.strip()

def create_map():
    print("Loading data...")
    df = pd.read_csv(CSV_PATH)
    
    # Identify Year
    year_cols = [c for c in df.columns if c.startswith('20')]
    latest_year = sorted(year_cols)[-1]
    print(f"Mapping Year: {latest_year}")
    
    # Normalize DF City
    df['City_Norm'] = df['City'].apply(normalize_turkish)
    data_map = df.set_index('City_Norm').to_dict('index')
    
    geo_data = None
    for url in GEOJSON_URLS:
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                geo_data = resp.json()
                break
        except: pass

    if not geo_data:
        print("GeoJSON download failed")
        return

    manual_map = {
        "Afyon": "Afyonkarahisar",
        "K. Maraş": "Kahramanmaraş",
        "Zongulda": "Zonguldak",
        "Elazig": "Elazığ"
    }

    for feature in geo_data['features']:
        props = feature['properties']
        city_name = props.get('name', '')
        
        if city_name in manual_map:
            norm_name = normalize_turkish(manual_map[city_name])
        else:
            norm_name = normalize_turkish(city_name)
            
        feature['id'] = norm_name
        
        if norm_name in data_map:
            row = data_map[norm_name]
            props['Avg_Household_Size'] = row[latest_year]
            props['City_Label'] = row['City']
        else:
            props['Avg_Household_Size'] = 0
            props['City_Label'] = city_name

    # Map
    m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
    
    cp = folium.Choropleth(
        geo_data=geo_data,
        name='Household Size',
        data=df,
        columns=['City_Norm', latest_year],
        key_on='feature.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Avg Household Size ({latest_year})',
        highlight=True
    ).add_to(m)
    
    folium.GeoJsonTooltip(
        fields=['City_Label', 'Avg_Household_Size'],
        aliases=['City:', 'Avg Size:'],
        localize=True
    ).add_to(cp.geojson)

    print(f"Saving {OUTPUT_HTML}...")
    m.save(OUTPUT_HTML)

if __name__ == "__main__":
    create_map()
