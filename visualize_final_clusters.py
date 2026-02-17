import pandas as pd
import folium
import requests
import json
import os

# Data Paths
CSV_PATH = "city_clusters_validated.csv"
GEOJSON_URLS = [
    "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/turkey.geojson",
    "https://raw.githubusercontent.com/volkansengul/turkey-geojson/master/turkey.json",
    "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json"
]
OUTPUT_HTML = "final_site_selection_map.html"

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
        if v.upper() in text: pass 
    normalization = {'I': 'I', 'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for k, v in normalization.items():
        text = text.replace(k, v)
    return text.strip()

def create_map():
    print("Loading Cluster Data...")
    df = pd.read_csv(CSV_PATH)
    
    # Check features to define labels
    # We need to manually interpret clusters based on IDs or pass description
    # For now, let's just color by ID (0,1,2,3)
    
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

    print("Merging...")
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
            props['Cluster'] = int(row['Cluster'])
            props['Cluster_Label'] = f"Profil {row['Cluster']}"
            props['Avg_Household_Size'] = row['Avg_Household_Size']
            props['Pct_Divorced'] = round(row['Pct_Divorced']*100, 2)
            props['Pct_Married'] = round(row['Pct_Married']*100, 2)
            props['City_Label'] = row['City']
        else:
            props['Cluster'] = -1
            props['Cluster_Label'] = "Veri Yok"
            props['City_Label'] = city_name

    # Map
    m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
    
    # Categorical Color Map
    # 4 Clusters -> 4 distinct colors
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3'] # Set1 colors
    
    def style_function(feature):
        c_id = feature['properties'].get('Cluster', -1)
        if c_id == -1: return {'fillColor': '#gray', 'color': 'gray', 'fillOpacity': 0.5}
        return {
            'fillColor': colors[c_id % len(colors)],
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    folium.GeoJson(
        geo_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['City_Label', 'Cluster_Label', 'Avg_Household_Size', 'Pct_Divorced', 'Pct_Married'],
            aliases=['Şehir:', 'Profil:', 'Hane Büyüklüğü:', 'Boşanma %:', 'Evlilik %:'],
            localize=True
        )
    ).add_to(m)
    
    # Add a Legend (Manual HTML)
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 160px; height: 130px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white; opacity: 0.9;">
     &nbsp;<b>Sosyal Profiller</b> <br>
     &nbsp;<i style="background:#e41a1c;width:10px;height:10px;display:inline-block;"></i>&nbsp;Profil 0<br>
     &nbsp;<i style="background:#377eb8;width:10px;height:10px;display:inline-block;"></i>&nbsp;Profil 1<br>
     &nbsp;<i style="background:#4daf4a;width:10px;height:10px;display:inline-block;"></i>&nbsp;Profil 2<br>
     &nbsp;<i style="background:#984ea3;width:10px;height:10px;display:inline-block;"></i>&nbsp;Profil 3<br>
     </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    print(f"Saving {OUTPUT_HTML}...")
    m.save(OUTPUT_HTML)

if __name__ == "__main__":
    create_map()
