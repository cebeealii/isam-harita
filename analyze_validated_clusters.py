import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load Data
df = pd.read_csv("city_demographics_validated_final.csv")

# Select Features for Clustering
# Select Features for Clustering
# 1. Avg_Household_Size (Family size)
# 2. Pct_Divorced (Standard Divorce Rate)
# 3. Pct_Never_Married (Young/Single population proxy)
features = ['Avg_Household_Size', 'Pct_Divorced', 'Pct_Never_Married']
X = df[features]

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Cluster (K=4, keeping consistent with previous analysis plan)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# Analyze Clusters
print("\n--- CLUSTER MEANS ---")
print(df.groupby('Cluster')[features].mean())

# Representative Cities
print("\n--- REPRESENTATIVE CITIES ---")
for i in range(4):
    print(f"\nCluster {i}:")
    print(df[df['Cluster'] == i]['City'].head(10).values)

# Save Analysis
df.to_csv("city_clusters_validated.csv", index=False)
print("\nSaved clustering results to city_clusters_validated.csv")
