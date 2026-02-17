import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv("city_demographics_final.csv")

# Select features for clustering
features = ['Avg_Household_Size', 'Median_Age', 'Dependency_Ratio', 'Pct_Single', 'Pct_Married', 'Pct_Divorced']

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

# Save results to Markdown
with open("analysis_report_generated.md", "w") as f:
    f.write("# Demographic Analysis & City Segmentation\n\n")
    f.write(f"Based on data from {len(df_clean)} cities.\n\n")
    
    f.write("## Cluster Profiles\n")
    for i in range(4):
        stats = cluster_stats.loc[i]
        reps = representatives[i]
        
        f.write(f"### Cluster {i}\n")
        f.write(f"**Representative Cities:** {', '.join(reps)}\n\n")
        f.write("**Characteristics:**\n")
        f.write(f"- Avg Household Size: {stats['Avg_Household_Size']:.2f}\n")
        f.write(f"- Median Age: {stats['Median_Age']:.1f}\n")
        f.write(f"- Dependency Ratio: {stats['Dependency_Ratio']:.1f}\n")
        f.write(f"- Single: {stats['Pct_Single']*100:.1f}%\n")
        f.write(f"- Married: {stats['Pct_Married']*100:.1f}%\n")
        f.write(f"- Divorced: {stats['Pct_Divorced']*100:.1f}%\n")
        f.write("\n")

print("Analysis complete. Report saved to analysis_report_generated.md")
