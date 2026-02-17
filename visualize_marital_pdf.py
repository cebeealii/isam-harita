import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Load Data
df = pd.read_csv("data_validated/marital_status_clean.csv")

# Filter for the latest year available per city (Data extraction script might have duplicates if multiple years existed)
# The extraction script didn't filter for year, it just took valid rows.
# Valid rows in that file likely are just one year block (2025 based on previous inspection).
# Let's drop duplicates just in case.
# The raw file has 2025 at the TOP. So we want keep='first'.
df = df.drop_duplicates(subset=['City'], keep='first')

# Calculate Percentages (if not already there or correct formatting)
# The CSV has Pct_Married, Pct_Divorced etc.

# Setup PDF
pdf_filename = "marital_status_report.pdf"
pp = PdfPages(pdf_filename)

# 1. Top 15 Cities by Divorce Rate (General)
plt.figure(figsize=(10, 6))
top_divorced = df.sort_values('Pct_Divorced', ascending=False).head(15)
sns.barplot(x='Pct_Divorced', y='City', data=top_divorced, palette='Reds_r')
plt.title('Top 15 Cities by Divorce Rate (% of Total 15+)')
plt.xlabel('Divorce Rate')
plt.tight_layout()
pp.savefig()
plt.close()

# 2. Bottom 15 Cities by Divorce Rate (General)
plt.figure(figsize=(10, 6))
low_divorced = df.sort_values('Pct_Divorced', ascending=True).head(15)
sns.barplot(x='Pct_Divorced', y='City', data=low_divorced, palette='Greens_r')
plt.title('Lowest 15 Cities by Divorce Rate (% of Total 15+)')
plt.xlabel('Divorce Rate')
plt.tight_layout()
pp.savefig()
plt.close()

# 3. Married vs Divorced Scatter
plt.figure(figsize=(10, 8))
sns.scatterplot(x='Pct_Married', y='Pct_Divorced', data=df)
# Label some points
for line in range(0, df.shape[0]):
    if df.iloc[line]['Pct_Divorced'] > 0.04 or df.iloc[line]['Pct_Married'] < 0.55:
        plt.text(df.iloc[line]['Pct_Married'], df.iloc[line]['Pct_Divorced'], df.iloc[line]['City'], horizontalalignment='left', size='small')
plt.title('Marriage Rate vs Divorce Rate (% of Total 15+)')
plt.xlabel('Marriage Rate (% of Total 15+)')
plt.ylabel('Divorce Rate (% of Total 15+)')
plt.tight_layout()
pp.savefig()
plt.close()

pp.close()
print(f"Generated PDF: {pdf_filename}")
