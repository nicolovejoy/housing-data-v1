# Railway Cloud Setup Guide

## Step 1: Create PostgreSQL Database on Railway

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Add a service" → "PostgreSQL"
4. Railway will create a PostgreSQL instance
5. Note the connection details shown in the dashboard

## Step 2: Get Database Connection String

In Railway dashboard:
1. Click on your PostgreSQL service
2. Go to "Connect" tab
3. Copy the **PostgreSQL URI** (looks like: `postgresql://user:password@host:port/database`)
4. Save this somewhere safe - you'll need it for Jupyter

**Alternative:** Click "Variables" and copy individual values:
- `PGHOST`
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`
- `PGDATABASE`

## Step 3: Create Database and Load Schema

From your local machine:

```bash
# Set connection string (replace with your actual Railway URI)
export DATABASE_URL="postgresql://user:password@host:port/database"

# Create schema in Railway
psql $DATABASE_URL < backend/db/init.sql

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

If `psql` isn't available locally, use Docker:
```bash
docker run --rm postgres:16 psql $DATABASE_URL -c "\dt"
```

## Step 4: Load FMR Data to Railway

First, install Python dependencies if not already done:
```bash
pip install psycopg2-binary python-dotenv
```

Then load the data:
```bash
# Set the DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run the data loader
python3 backend/scripts/load_fmr_data.py
```

This will:
- Read `fmr_data.json`
- Insert all 5,449 areas into Railway PostgreSQL
- Insert rent data for each area
- Show verification statistics

## Step 5: Verify Data in Railway

```bash
# Check area count
psql $DATABASE_URL -c "SELECT COUNT(*) FROM areas;"
# Should return: 5449

# Check state distribution
psql $DATABASE_URL -c "
SELECT state, COUNT(*) as count
FROM areas
GROUP BY state
ORDER BY count DESC LIMIT 10;"

# Test pivot view
psql $DATABASE_URL -c "
SELECT * FROM pivot_by_state_type
WHERE state IN ('CA', 'NY', 'TX');"
```

## Step 6: Save Connection Info for Jupyter

Create a `.env` file in the project root (or use in Jupyter):

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

Or for Jupyter, you can directly use:
```python
import os
os.environ['DATABASE_URL'] = 'postgresql://user:password@host:port/database'
```

---

## Troubleshooting

### Can't connect to Railway PostgreSQL

```bash
# Test connection with psql
psql postgresql://user:password@host:port/database -c "SELECT 1"

# If times out, check:
# 1. Connection string is correct (copy from Railway dashboard again)
# 2. Railway PostgreSQL is running (check dashboard)
# 3. Your internet/firewall allows outbound port 5432
```

### Schema creation failed

```bash
# Check if tables exist
psql $DATABASE_URL -c "\dt"

# If they don't, manually run the schema in Railway
# Via Railway dashboard → PostgreSQL → "Shell" tab
# Paste the contents of backend/db/init.sql
```

### Data loading failed

```bash
# Check if fmr_data.json exists and is valid
ls -lah fmr_data.json
jq . fmr_data.json | head  # Show first few lines

# If file is missing, run:
python3 explore_fmr.py

# Then retry loading
python3 backend/scripts/load_fmr_data.py
```

---

## Next: Jupyter Notebook Setup

Once data is loaded in Railway:

1. Install Jupyter: `pip install jupyter pandas psycopg2-binary sqlalchemy`
2. Create notebook: `jupyter notebook`
3. Connect to Railway database:

```python
import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@host:port/database"

# Method 1: Using psycopg2
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("SELECT * FROM areas LIMIT 5")
for row in cursor.fetchall():
    print(row)

# Method 2: Using SQLAlchemy + Pandas (recommended)
engine = create_engine(DATABASE_URL)
df = pd.read_sql("SELECT * FROM areas LIMIT 5", engine)
print(df)
```

---

## Railway Commands (CLI)

If you prefer command line:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# View environment variables
railway variables

# View database connection
railway status
```

---

## Success Criteria

✅ PostgreSQL service running on Railway
✅ Schema created (tables exist)
✅ 5,449 areas loaded
✅ Query results match local expectations
✅ Connection string works from local machine
✅ Can connect from Jupyter notebook
