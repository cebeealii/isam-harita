import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load Data
df = pd.read_csv("city_demographics_validated_final.csv")

# Select Features for Clustering
# Features (Check column names first)
# Use 'Pct_Single' if 'Pct_Never_Married' is missing
if 'Pct_Never_Married' not in df.columns and 'Pct_Single' in df.columns:
    df.rename(columns={'Pct_Single': 'Pct_Never_Married'}, inplace=True)

features = ['Avg_Household_Size', 'Pct_Divorced', 'Pct_Never_Married']
X = df[features].dropna()

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Cluster
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df.loc[X.index, 'Cluster'] = kmeans.fit_predict(X_scaled)

# Calculate Means
means = df.groupby('Cluster')[features].mean()

# GENERATE REPORT
report = []
report.append("NİTEL ARAŞTIRMA SAHA SEÇİM RAPORU (DETAYLI ANALİZ)")
report.append("="*50)
report.append("\nBu rapor, şehirleri demografik özelliklerine göre (Hane büyüklüğü, Boşanma, Bekarlık) 4 ana gruba ayırır.\n")

report.append("1. KÜME ORTALAMALARI (YÜZDELER)")
report.append("-" * 30)
# Format the table manually for text file
report.append(f"{'Küme':<5} {'Hane Büy.':<12} {'Boşanma %':<12} {'Bekar %':<12}")
for i, row in means.iterrows():
    report.append(f"{i:<5} {row['Avg_Household_Size']:<12.2f} {row['Pct_Divorced']*100:<12.1f} {row['Pct_Never_Married']*100:<12.1f}")
report.append("-" * 30)
report.append("*Değerler ortalamadır. Boşanma ve Bekar oranları yüzde (%) cinsindendir.\n")

report.append("2. PROFİL DETAYLARI VE ŞEHİR ÖNERİLERİ")
report.append("=" * 50)

for i in range(4):
    stats = means.loc[i]
    
    # Naming Logic
    name = f"Profil {i+1}"
    characteristics = []
    
    if stats['Avg_Household_Size'] > 3.8: characteristics.append("Geniş Aile")
    elif stats['Avg_Household_Size'] < 3.0: characteristics.append("Çekirdek/Küçük Aile")
    
    if stats['Pct_Divorced'] > 0.025: characteristics.append("Yüksek Boşanma")
    elif stats['Pct_Divorced'] < 0.01: characteristics.append("Düşük Boşanma")
    
    if stats['Pct_Never_Married'] > 0.30: characteristics.append("Genç/Bekar Nüfus")
    
    if characteristics:
        name += f": {' & '.join(characteristics)}"
        
    cities = df[df['Cluster'] == i]['City'].values
    sample_cities = cities[:5] 
    
    report.append(f"\n### {name}")
    report.append(f"Özet: Ort. Hane: {stats['Avg_Household_Size']:.1f}, Boşanma: %{stats['Pct_Divorced']*100:.1f}, Bekar: %{stats['Pct_Never_Married']*100:.1f}")
    report.append("\nÖnerilen Şehirler (Örnekler):")
    for c in sample_cities:
        report.append(f"  * {c}")

# Save to file
with open("Nitel_Arastirma_Raporu_Detayli.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("Detailed report generated: Nitel_Arastirma_Raporu_Detayli.txt")
