import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Load Data
df = pd.read_csv("data_validated/household_size_clean.csv")

# Identify the latest year column
# Columns: City, 2023, 2024, 2025...
year_cols = [c for c in df.columns if c.startswith('20')]
latest_year = sorted(year_cols)[-1]
print(f"Visualizing for Year: {latest_year}")

# Setup PDF
pdf_filename = "household_size_report.pdf"
pp = PdfPages(pdf_filename)

# 1. Top 15 Cities by Household Size
plt.figure(figsize=(10, 6))
top_house = df.sort_values(latest_year, ascending=False).head(15)
sns.barplot(x=latest_year, y='City', data=top_house, palette='Oranges_r')
plt.title(f'Top 15 Cities by Average Household Size ({latest_year})')
plt.xlabel('Persons per Household')
plt.tight_layout()
pp.savefig()
plt.close()

# 2. Bottom 15 Cities by Household Size
plt.figure(figsize=(10, 6))
low_house = df.sort_values(latest_year, ascending=True).head(15)
sns.barplot(x=latest_year, y='City', data=low_house, palette='Blues_r')
plt.title(f'Smallest 15 Cities by Average Household Size ({latest_year})')
plt.xlabel('Persons per Household')
plt.tight_layout()
pp.savefig()
plt.close()

# 3. Distribution
plt.figure(figsize=(10, 6))
sns.histplot(df[latest_year], bins=20, kde=True)
plt.title(f'Distribution of Average Household Size ({latest_year})')
plt.xlabel('Persons per Household')
plt.tight_layout()
pp.savefig()
plt.close()

pp.close()
print(f"Generated PDF: {pdf_filename}")
