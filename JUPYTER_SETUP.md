# Jupyter Notebook Setup for FMR Data Exploration

## Installation

```bash
# Install Jupyter and required libraries
pip install jupyter pandas psycopg2-binary sqlalchemy matplotlib seaborn

# Start Jupyter
jupyter notebook
```

This will open a browser window at `http://localhost:8888`

## Quick Start

1. Create a new notebook: "New" → "Python 3"
2. In the first cell, add your Railway database connection
3. Start exploring!

## Basic Connection Template

```python
import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns

# Your Railway PostgreSQL connection string
# Get this from Railway dashboard → PostgreSQL → Connect
DATABASE_URL = "postgresql://user:password@host:port/database"

# Create SQLAlchemy engine (easiest way to work with data)
engine = create_engine(DATABASE_URL)

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM areas"))
        count = result.fetchone()[0]
        print(f"✅ Connected! Database has {count:,} areas")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Example Queries

### Load all data as DataFrame

```python
# Load all areas with rent data
df = pd.read_sql("SELECT * FROM areas_with_rents", engine)
print(f"Loaded {len(df)} areas")
print(df.head())
```

### Pivot analysis by state and type

```python
pivot_df = pd.read_sql("SELECT * FROM pivot_by_state_type", engine)
print(pivot_df.head(10))

# Show states with most areas
pivot_df.groupby('state')['count'].sum().sort_values(ascending=False).head(10)
```

### Overall statistics

```python
stats_df = pd.read_sql("SELECT * FROM overall_stats", engine)
print(stats_df)
```

### Find most expensive areas

```python
expensive = pd.read_sql("""
    SELECT
        name,
        state,
        type,
        studio_rent,
        one_bedroom_rent,
        two_bedroom_rent,
        three_bedroom_rent,
        four_bedroom_rent
    FROM areas_with_rents
    WHERE two_bedroom_rent > 0
    ORDER BY two_bedroom_rent DESC
    LIMIT 20
""", engine)

print(expensive)
```

### Find most affordable areas

```python
affordable = pd.read_sql("""
    SELECT
        name,
        state,
        type,
        studio_rent,
        one_bedroom_rent,
        two_bedroom_rent,
        three_bedroom_rent,
        four_bedroom_rent
    FROM areas_with_rents
    WHERE two_bedroom_rent > 0
    ORDER BY two_bedroom_rent ASC
    LIMIT 20
""", engine)

print(affordable)
```

### Analyze by state

```python
state_stats = pd.read_sql("""
    SELECT
        state,
        type,
        COUNT(*) as count,
        AVG(two_bedroom_rent)::INT as avg_2br,
        MIN(two_bedroom_rent) as min_2br,
        MAX(two_bedroom_rent) as max_2br
    FROM areas_with_rents
    WHERE two_bedroom_rent > 0
    GROUP BY state, type
    ORDER BY state, type
""", engine)

print(state_stats)

# Pivot to compare metros vs counties by state
pivot = state_stats.pivot_table(index='state', columns='type', values=['count', 'avg_2br'])
pivot
```

## Visualization Examples

### Histogram of 2-bedroom rents

```python
df = pd.read_sql("""
    SELECT two_bedroom_rent FROM areas_with_rents
    WHERE two_bedroom_rent > 0
""", engine)

plt.figure(figsize=(12, 6))
plt.hist(df['two_bedroom_rent'], bins=50, edgecolor='black', alpha=0.7)
plt.xlabel('2-Bedroom Monthly Rent ($)')
plt.ylabel('Number of Areas')
plt.title('Distribution of 2-Bedroom Fair Market Rents')
plt.grid(True, alpha=0.3)
plt.show()
```

### Scatter: Studio vs 2-Bedroom

```python
df = pd.read_sql("""
    SELECT studio_rent, two_bedroom_rent FROM areas_with_rents
    WHERE studio_rent > 0 AND two_bedroom_rent > 0
""", engine)

plt.figure(figsize=(10, 8))
plt.scatter(df['studio_rent'], df['two_bedroom_rent'], alpha=0.6, s=30)
plt.xlabel('Studio Rent ($)')
plt.ylabel('2-Bedroom Rent ($)')
plt.title('Studio vs 2-Bedroom Fair Market Rents')
plt.grid(True, alpha=0.3)
plt.show()

# Calculate correlation
print(f"Correlation: {df['studio_rent'].corr(df['two_bedroom_rent']):.3f}")
```

### Bar chart: Top 10 states by average rent

```python
state_avg = pd.read_sql("""
    SELECT
        state,
        AVG(two_bedroom_rent)::INT as avg_2br
    FROM areas_with_rents
    WHERE two_bedroom_rent > 0
    GROUP BY state
    ORDER BY avg_2br DESC
    LIMIT 10
""", engine)

plt.figure(figsize=(10, 6))
plt.barh(state_avg['state'], state_avg['avg_2br'])
plt.xlabel('Average 2-Bedroom Rent ($)')
plt.title('Top 10 States by Average 2-Bedroom Rent')
plt.grid(True, alpha=0.3, axis='x')
plt.show()
```

## Next Steps in Jupyter

Once you're comfortable with the data:

1. **Explore patterns:**
   - Which states/metros are most expensive?
   - How much do rents increase by bedroom size?
   - What's the relationship between area type (metro vs county) and rent?

2. **Prepare for multi-dataset integration:**
   - Identify what additional data would be valuable
   - Think about Census data, income data, demographics
   - Plan how to join/normalize external datasets

3. **Document findings:**
   - Create visualizations
   - Write analysis summaries
   - Note interesting patterns for the Next.js UI

4. **Prepare schema updates:**
   - Plan new tables for additional datasets
   - Design normalized schema for combining data

---

## Tips

- Use `%%time` at the start of a cell to time execution
- Use `df.info()` to see column types and missing values
- Use `df.describe()` for statistical summaries
- Save plots with `plt.savefig('filename.png', dpi=300)`
- Use `# %%` to divide notebook into sections (Jupyter cells)

## Troubleshooting

### Connection timeout
```python
# Make sure DATABASE_URL is correct
# Copy from Railway dashboard again
# Check internet/firewall allows port 5432
```

### ModuleNotFoundError
```bash
# Install missing module
pip install <module_name>

# For example:
pip install sqlalchemy
```

### No data returned
```python
# Check row counts
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM areas"))
    print(result.fetchone()[0])

# If 0, data wasn't loaded
# Run: python3 backend/scripts/load_fmr_data.py
```
