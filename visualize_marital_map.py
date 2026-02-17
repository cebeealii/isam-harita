import pandas as pd
import folium
import requests
import json
import os

# Data Paths
CSV_PATH = "data_validated/marital_status_clean.csv"
GEOJSON_URLS = [
    "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/turkey.geojson",
    "https://raw.githubusercontent.com/volkansengul/turkey-geojson/master/turkey.json",
    "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json"
]
OUTPUT_HTML = "marital_status_map.html"

def normalize_turkish(text):
    """Normalize Turkish characters for matching."""
    if not isinstance(text, str): return str(text)
    mapping = {
        'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 
        'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 
        'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
    }
    # Special handling for I/i which is tricky
    text = text.replace("İ", "I").upper()
    for k, v in mapping.items():
        if k in text: text = text.replace(k, v)
        if v.upper() in text: pass # already upper
    
    normalization = {
        'I': 'I', 'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'
    }
    for k, v in normalization.items():
        text = text.replace(k, v)
        
    return text.strip()

def create_map():
    print("Loading data...")
    df = pd.read_csv(CSV_PATH)
    # Deduplicate just in case
    # The raw file has 2025 at the TOP. So we want keep='first'.
    df = df.drop_duplicates(subset=['City'], keep='first')
    
    # Normalize DF City
    df['City_Norm'] = df['City'].apply(normalize_turkish)
    data_map = df.set_index('City_Norm').to_dict('index')
    
    geo_data = None
    for url in GEOJSON_URLS:
        print(f"Downloading GeoJSON: {url}")
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                geo_data = resp.json()
                print("Download successful.")
                break
        except Exception as e:
            print(f"Error: {e}")
            
    if not geo_data:
        print("Could not download GeoJSON.")
        return

    # Manual Mapping
    manual_map = {
        "Afyon": "Afyonkarahisar",
        "K. Maraş": "Kahramanmaraş",
        "Zongulda": "Zonguldak",
        "Elazig": "Elazığ"
    }

    print("Merging data...")
    for feature in geo_data['features']:
        props = feature['properties']
        city_name = props.get('name', '')
        
        if city_name in manual_map:
            true_name = manual_map[city_name]
            norm_name = normalize_turkish(true_name)
        else:
            norm_name = normalize_turkish(city_name)
            
        feature['id'] = norm_name
        props['name_norm'] = norm_name

        if norm_name in data_map:
            row = data_map[norm_name]
            # Use Standard Rate
            props['Pct_Divorced'] = round(row.get('Pct_Divorced', 0)*100, 2)
            props['Pct_Married'] = round(row.get('Pct_Married', 0)*100, 2)
            props['Pct_Never_Married'] = round(row.get('Pct_Never_Married', 0)*100, 2)
            props['City_Label'] = row.get('City')
        else:
            props['Pct_Divorced'] = 0
            props['City_Label'] = city_name

    # Initialize Map
    m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
    
    # Layer: Divorce Rate
    cp_div = folium.Choropleth(
        geo_data=geo_data,
        name='Divorce Rate (%)',
        data=df,
        columns=['City_Norm', 'Pct_Divorced'],
        key_on='feature.id',
        fill_color='PuRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Divorce Rate (2025) %',
        highlight=True
    ).add_to(m)
    
    # Tooltips
    folium.GeoJsonTooltip(
        fields=['City_Label', 'Pct_Divorced', 'Pct_Married', 'Pct_Never_Married'],
        aliases=['City:', 'Divorced %:', 'Married %:', 'Never Married %:'],
        localize=True
    ).add_to(cp_div.geojson)

    folium.LayerControl().add_to(m)
    
    print(f"Saving map to {OUTPUT_HTML}...")
    m.save(OUTPUT_HTML)
    print("Done.")

if __name__ == "__main__":
    create_map()
