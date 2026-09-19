import pandas as pd
import seaborn as sns
import numpy as np

# Load dataset once and save offline fallback
df = sns.load_dataset('titanic')
df.to_csv("titanic.csv", index=False)

print("Dataset Info:")
df.info()

print("\nMissing Value Percentages:")
missing_pct = df.isnull().mean() * 100
print(missing_pct[missing_pct > 0])

# Outlier Detection via IQR
for col in ['age', 'fare']:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]
    print(f"Outliers in {col}: {len(outliers)}")

# Skewness check for fare
print(f"Fare Mean: {df['fare'].mean():.2f}, Median: {df['fare'].median():.2f}, Mode: {df['fare'].mode()[0]:.2f}")