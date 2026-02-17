import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv("city_demographics_final.csv")

# Select features for clustering
features = ['Avg_Household_Size', 'Median_Age', 'Pct_Single', 'Pct_Married', 'Pct_Divorced']

# Drop rows with missing values
df_clean = df.dropna(subset=features)
print(f"Data for analysis: {len(df_clean)} cities (Original: {len(df)})")

# Normalize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_clean[features])

# Clustering (K=4 for now)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_clean['Cluster'] = kmeans.fit_predict(X_scaled)

# Analysis of Clusters
numeric_cols = features + ['Cluster']
cluster_stats = df_clean[numeric_cols].groupby('Cluster').mean()
print("\nCluster Averages:")
print(cluster_stats)

# Find representative cities for each cluster
# (Closest to center)
representatives = {}
for i in range(4):
    center = kmeans.cluster_centers_[i]
    # Calculate distance of each point in this cluster to center
    cluster_indices = df_clean[df_clean['Cluster'] == i].index
    cluster_data = X_scaled[df_clean.index.get_indexer(cluster_indices)]
    distances = np.linalg.norm(cluster_data - center, axis=1)
    # Get top 3 closest
    closest_indices = distances.argsort()[:5]
    cities = df_clean.loc[cluster_indices[closest_indices], 'City'].values
    representatives[i] = cities

print("\nRepresentative Cities:")
for i, cities in representatives.items():
    print(f"Cluster {i}: {', '.join(cities)}")

# Save results to Markdown with Qualitative Focus (Turkish)
with open("analysis_report_generated.md", "w", encoding="utf-8") as f:
    f.write("# Nitel Araştırma İçin Saha Seçim Stratejisi\n\n")
    f.write(f"**Amaç:** {len(df_clean)} şehir arasından, nitel saha çalışması için farklı demografik profilleri temsil eden şehirleri belirlemek.\n\n")
    f.write(f"**Kullanılan Veriler:** Ortalama Hanehalkı Büyüklüğü, Ortanca Yaş, Medeni Durum (Bekar/Evli/Boşanmış). *Bağımlılık Oranı (hatalı veri) hariç tutulmuştur.*\n\n")
    
    f.write("## Belirlenen Araştırma Profilleri\n")
    for i in range(4):
        stats = cluster_stats.loc[i]
        reps = representatives[i]
        
        # Determine a descriptive name based on stats (Turkish)
        name = f"Profil {i+1}"
        desc = []
        justification = ""
        
        if stats['Avg_Household_Size'] > 3.8: 
            desc.append("Geniş Aileler")
            justification += "Geleneksel geniş aile yapısını ve akrabalık ilişkilerini incelemek için idealdir. "
        elif stats['Avg_Household_Size'] < 2.9: 
            desc.append("Çekirdek/Küçük Haneler")
            justification += "Bireyselleşme ve modern çekirdek aile dinamiklerini gözlemlemek için uygundur. "
        
        if stats['Median_Age'] < 30: 
            desc.append("Genç Nüfus")
            justification += "Gençlerin hayata bakışını ve eğitim/iş beklentilerini anlamak için seçilmelidir. "
        elif stats['Median_Age'] > 37: 
            desc.append("Olgun Nüfus")
            justification += "Yaşlanan nüfusun ihtiyaçlarını ve kuşak çatışmalarını incelemek için elverişlidir. "
        
        if stats['Pct_Single'] > 0.30: 
            desc.append("Yüksek Bekar Oranı")
        if stats['Pct_Divorced'] > 0.025: 
            desc.append("Yüksek Boşanma Oranı")
            justification += "Değişen aile yapısı ve boşanma sonrası yaşam pratiklerini araştırmak için önemlidir. "
            
        if not justification:
            justification = "Ortalama Türkiye demografisini temsil eden standart bir profil."
        
        if desc: name = f"Profil {i+1}: {' & '.join(desc)}"
        
        f.write(f"### {name}\n")
        f.write(f"**Neden Bu Profil Seçilmeli?**\n")
        f.write(f"{justification}\n\n")
        
        f.write(f"**Hedef Demografi Özellikleri:**\n")
        f.write(f"- Hane Yapısı: {'Geniş (>3.8)' if stats['Avg_Household_Size'] > 3.8 else 'Standart/Küçük'}\n")
        f.write(f"- Yaş Grubu: {'Genç (<30)' if stats['Median_Age'] < 30 else 'Olgun (>37)' if stats['Median_Age'] > 37 else 'Orta Yaş'}\n")
        f.write(f"- Medeni Durum: %{stats['Pct_Married']*100:.1f} Evli, %{stats['Pct_Divorced']*100:.1f} Boşanmış\n\n")
        
        f.write(f"**Önerilen Saha Şehirleri (Temsili):**\n")
        for city in reps[:3]:
            f.write(f"- **{city}**\n")
        f.write("\n")
        f.write("---\n")

print("Analysis complete. Report saved to analysis_report_generated.md")
