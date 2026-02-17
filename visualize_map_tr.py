import pandas as pd
import folium
import requests
import json
import os

# Data Paths
CSV_PATH = "city_demographics_final.csv"
GEOJSON_URLS = [
    "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/turkey.geojson",
    "https://raw.githubusercontent.com/volkansengul/turkey-geojson/master/turkey.json",
    "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json"
]
OUTPUT_HTML = "turkiye_aile_arastirmasi_haritasi.html"

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
    print("Veri yukleniyor (Loading data)...")
    df = pd.read_csv(CSV_PATH)
    
    # Normalize DF City
    df['City_Norm'] = df['City'].apply(normalize_turkish)
    data_map = df.set_index('City_Norm').to_dict('index')
    
    geo_data = None
    for url in GEOJSON_URLS:
        print(f"GeoJSON indiriliyor: {url}")
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                geo_data = resp.json()
                print("Indirme basarili (Download successful).")
                break
            else:
                print(f"Hata Kodu: {resp.status_code}")
        except Exception as e:
            print(f"Hata: {e}")
            
    if not geo_data:
        print("GeoJSON indirilemedi. Cikis yapiliyor.")
        return

    # Manual Mapping for specific mismatches
    manual_map = {
        "Afyon": "Afyonkarahisar",
        "K. Maraş": "Kahramanmaraş",
        "Zongulda": "Zonguldak",
        "Elazig": "Elazığ"
    }

    print("Veriler birlestiriliyor (Merging data)...")
    found_count = 0
    
    for feature in geo_data['features']:
        props = feature['properties']
        city_name = props.get('name', '')
        
        # Apply manual map if needed
        if city_name in manual_map:
            true_name = manual_map[city_name]
            norm_name = normalize_turkish(true_name)
        else:
            norm_name = normalize_turkish(city_name)
            
        # Set ID for folium linking
        feature['id'] = norm_name
        props['name_norm'] = norm_name

        # Try to find in data
        if norm_name in data_map:
            row = data_map[norm_name]
            props['Avg_Household_Size'] = round(row.get('Avg_Household_Size', 0), 2)
            props['Median_Age'] = round(row.get('Median_Age', 0), 1)
            props['Dependency_Ratio'] = 0 # Removed as requested
            props['Pct_Married'] = round(row.get('Pct_Married', 0) * 100, 1) if pd.notna(row.get('Pct_Married')) else 'N/A'
            found_count += 1
        else:
            props['Avg_Household_Size'] = 0
            props['Median_Age'] = 0
            props['Dependency_Ratio'] = 0
            print(f"  Eşleşmeyen Şehir: {city_name} (Norm: {norm_name})")

    print(f"Eşleşen şehir sayısı: {found_count} / {len(geo_data['features'])}")

    # Initialize Map
    m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
    
    # Create Choropleth layer with Turkish Legend
    cp = folium.Choropleth(
        geo_data=geo_data,
        name='Hanehalkı Büyüklüğü',
        data=df,
        columns=['City_Norm', 'Avg_Household_Size'],
        key_on='feature.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Ortalama Hanehalkı Büyüklüğü',
        highlight=True
    ).add_to(m)
    
    # Add Tooltip with Turkish Labels
    folium.GeoJsonTooltip(
        fields=['name', 'Avg_Household_Size', 'Median_Age', 'Pct_Married'],
        aliases=['Şehir:', 'Ort. Hane Büyüklüğü:', 'Ortanca Yaş:', 'Evlilik Oranı %:'],
        localize=True
    ).add_to(cp.geojson)

    folium.LayerControl().add_to(m)
    
    print(f"Harita kaydediliyor: {OUTPUT_HTML}...")
    m.save(OUTPUT_HTML)
    print("Tamamlandı.")

if __name__ == "__main__":
    create_map()
