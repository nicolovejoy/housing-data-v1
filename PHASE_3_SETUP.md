# Phase 3: Database Setup & Data Loading

## Quick Start

This guide walks you through setting up PostgreSQL and loading the FMR data.

### Step 1: Start PostgreSQL with Docker

```bash
docker-compose up -d postgres
```

Verify it's running:
```bash
docker-compose ps
# Should show postgres as "Up"
```

### Step 2: Create Database Schema

```bash
# Connect to PostgreSQL and run the schema script
psql postgresql://postgres:postgres@localhost:5432 < backend/db/init.sql
```

If `psql` is not in your PATH, you can use:
```bash
docker-compose exec postgres psql -U postgres -d fmr_data < backend/db/init.sql
```

### Step 3: Verify Schema Created

```bash
# List tables
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "\dt"

# Should show:
#  public | areas      | table | postgres
#  public | rents      | table | postgres
#  public | aggregations | table | postgres
```

### Step 4: Generate FMR Data (if not done already)

Make sure `fmr_data.json` exists:

```bash
python3 explore_fmr.py
```

This creates `fmr_data.json` with all 5,449 areas.

### Step 5: Load Data into Database

#### Option A: Using psql (Simple)

```bash
# Get the count before loading
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "SELECT COUNT(*) FROM areas;"
# Should return 0

# Create a simple SQL script to load the JSON data
# (requires jq or similar to parse JSON)
```

#### Option B: Using Python script (Recommended)

```bash
cd backend/scripts
python3 load_fmr_data.py
```

This will:
- Read `fmr_data.json`
- Parse each area
- Insert into PostgreSQL
- Show progress

### Step 6: Verify Data Loaded

```bash
# Check total area count
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "SELECT COUNT(*) FROM areas;"
# Should return 5449

# Check state distribution
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "
SELECT state, COUNT(*) as count
FROM areas
GROUP BY state
ORDER BY count DESC
LIMIT 10;"

# Check min/max rents
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "
SELECT
  MIN(two_bedroom_rent) as min_rent,
  MAX(two_bedroom_rent) as max_rent,
  AVG(two_bedroom_rent)::INT as avg_rent
FROM rents;"
```

### Step 7: Test Pivot Queries

```bash
# Query pivot by state and type
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "
SELECT * FROM pivot_by_state_type
WHERE state IN ('CA', 'NY', 'TX');"

# Query overall stats
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "
SELECT * FROM overall_stats;"
```

---

## Checkpoint 3A: Schema Created ✓

Verify:
```bash
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "\dt"
```

**Expected Output:**
```
           List of relations
 Schema | Name | Type | Owner
--------+------+------+----------
 public | aggregations | table | postgres
 public | areas | table | postgres
 public | rents | table | postgres
(3 rows)
```

---

## Checkpoint 3B: Data Loaded ✓

Verify:
```bash
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "SELECT COUNT(*) FROM areas;"
```

**Expected Output:** `5449`

```bash
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "SELECT COUNT(*) FROM rents;"
```

**Expected Output:** `5449`

---

## Checkpoint 3C: Data Queries Work ✓

Run this query to verify data integrity:

```bash
psql postgresql://postgres:postgres@localhost:5432/fmr_data << 'EOF'
-- Check state breakdown
SELECT state, COUNT(*) as count
FROM areas
GROUP BY state
ORDER BY count DESC
LIMIT 10;

-- Check type breakdown
SELECT type, COUNT(*) as count
FROM areas
GROUP BY type;

-- Check rent statistics
SELECT
  MIN(two_bedroom_rent) as min_rent,
  MAX(two_bedroom_rent) as max_rent,
  ROUND(AVG(two_bedroom_rent)::NUMERIC, 2) as avg_rent,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY two_bedroom_rent) as median_rent
FROM rents
WHERE two_bedroom_rent > 0;
EOF
```

**Expected Output:**
- Top states: CA, TX, NY, FL, etc. with 30-100+ areas each
- Type breakdown: ~3500 counties, ~1900 metros
- Rents: min=$473, max=$4054, avg≈$1214, median≈$1068

---

## Troubleshooting

### Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### psql Not Found

If `psql` command not found, use Docker instead:

```bash
docker-compose exec postgres psql -U postgres -d fmr_data -c "SELECT COUNT(*) FROM areas;"
```

### Data Not Loading

- Verify `fmr_data.json` exists: `ls -la fmr_data.json`
- Check file size is > 1MB: `du -h fmr_data.json`
- Verify JSON is valid: `jq . fmr_data.json | head`

### Wrong Data Counts

If counts are wrong, reset and reload:

```bash
# Drop all data (careful!)
docker-compose exec postgres psql -U postgres -d fmr_data -c "DROP TABLE IF EXISTS rents CASCADE; DROP TABLE IF EXISTS areas CASCADE;"

# Re-run schema
psql postgresql://postgres:postgres@localhost:5432 < backend/db/init.sql

# Reload data
python3 backend/scripts/load_fmr_data.py
```

---

## Next Steps

Once Phase 3 is complete:
1. Verify all 3 checkpoints pass ✓
2. Commit to git: `git add . && git commit -m "Phase 3 complete: Database schema and data loaded"`
3. Push to GitHub: `git push`
4. Switch to Jupyter notebooks for exploratory analysis

---

## Database Structure Reference

### tables

**areas** - Geographic areas
```
id (UUID)           - Primary key
name (VARCHAR)      - Area name
type (VARCHAR)      - 'metro' or 'county'
state (VARCHAR)     - Two-letter state code
state_name (VARCHAR)- Full state name
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**rents** - Rent data for each area
```
id (UUID)           - Primary key
area_id (UUID)      - Foreign key to areas
studio_rent (INTEGER)
one_bedroom_rent (INTEGER)
two_bedroom_rent (INTEGER)
three_bedroom_rent (INTEGER)
four_bedroom_rent (INTEGER)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**aggregations** - Pre-computed pivot tables
```
id (UUID)           - Primary key
group_by (TEXT)     - Grouping fields
state (VARCHAR)     - Filter: state
type (VARCHAR)      - Filter: metro/county
count (INTEGER)     - Number of areas
avg_* (NUMERIC)     - Average rents by bedroom
min/max_two_br (INTEGER) - Range
created_at (TIMESTAMP)
```

### Views (Queryable)

- **areas_with_rents** - JOIN areas + rents in one view
- **pivot_by_state_type** - Pre-aggregated by state + type
- **overall_stats** - National statistics

---

## Commands Summary

```bash
# Start database
docker-compose up -d postgres

# Create schema
psql postgresql://postgres:postgres@localhost:5432 < backend/db/init.sql

# Verify schema
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "\dt"

# Load data
python3 backend/scripts/load_fmr_data.py

# Verify data count
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "SELECT COUNT(*) FROM areas;"

# Test pivot query
psql postgresql://postgres:postgres@localhost:5432/fmr_data -c "SELECT * FROM pivot_by_state_type LIMIT 5;"

# Stop database
docker-compose down
```
