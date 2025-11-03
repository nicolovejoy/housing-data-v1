#!/usr/bin/env python3
"""
Load FMR data from fmr_data.json into PostgreSQL database

Usage:
    python3 backend/scripts/load_fmr_data.py

Requirements:
    - PostgreSQL running (docker-compose up -d postgres)
    - Schema created (psql < backend/db/init.sql)
    - fmr_data.json exists (run explore_fmr.py first)
"""

import json
import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    print("❌ psycopg2 not installed")
    print("   Install with: pip install psycopg2-binary")
    sys.exit(1)


def get_connection():
    """Create PostgreSQL connection"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        # Build from individual env vars
        db_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'fmr_data')}"

    try:
        conn = psycopg2.connect(db_url)
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\nMake sure PostgreSQL is running:")
        print("  docker-compose up -d postgres")
        sys.exit(1)


def load_data():
    """Load FMR data from JSON into PostgreSQL"""

    # Read fmr_data.json
    data_path = Path(__file__).parent.parent.parent / 'fmr_data.json'
    if not data_path.exists():
        print(f"❌ {data_path} not found!")
        print("   Run: python3 explore_fmr.py")
        sys.exit(1)

    print(f"📖 Reading {data_path}...")
    with open(data_path, 'r') as f:
        data = json.load(f)

    areas = data.get('areas', [])
    print(f"✅ Loaded {len(areas)} areas from JSON")

    # Connect to database
    print("🔌 Connecting to PostgreSQL...")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Prepare batch inserts
        area_inserts = []
        rent_inserts = []

        for area in areas:
            # Areas table
            area_inserts.append((
                area['name'],
                area['type'],
                area['state'],
                area.get('state_name', '')
            ))

            # Rents table (will join by area name)
            rent_inserts.append((
                area['name'],
                area['state'],
                area.get('studio_rent'),
                area.get('one_bedroom_rent'),
                area.get('two_bedroom_rent'),
                area.get('three_bedroom_rent'),
                area.get('four_bedroom_rent'),
            ))

        # Insert areas
        print("\n📊 Inserting areas...")
        area_query = "INSERT INTO areas (name, type, state, state_name) VALUES (%s, %s, %s, %s)"
        execute_batch(cursor, area_query, area_inserts, page_size=1000)
        print(f"   ✅ Inserted {len(area_inserts)} areas")

        # Insert rents (matching by name and state)
        print("\n📊 Inserting rents...")
        rent_query = """
            INSERT INTO rents (area_id, studio_rent, one_bedroom_rent, two_bedroom_rent, three_bedroom_rent, four_bedroom_rent)
            SELECT id, %s, %s, %s, %s, %s
            FROM areas
            WHERE name = %s AND state = %s
        """

        # Need to do rents one-by-one to get the correct area_id
        for rent_data in rent_inserts:
            name, state, studio, one_br, two_br, three_br, four_br = rent_data
            cursor.execute(
                rent_query,
                (studio, one_br, two_br, three_br, four_br, name, state)
            )

        print(f"   ✅ Inserted {len(rent_inserts)} rent records")

        # Verify
        print("\n✅ Verifying data...")
        cursor.execute("SELECT COUNT(*) FROM areas")
        area_count = cursor.fetchone()[0]
        print(f"   Areas: {area_count:,}")

        cursor.execute("SELECT COUNT(*) FROM rents")
        rent_count = cursor.fetchone()[0]
        print(f"   Rents: {rent_count:,}")

        # Get statistics
        cursor.execute("""
            SELECT
                MIN(two_bedroom_rent) as min_rent,
                MAX(two_bedroom_rent) as max_rent,
                ROUND(AVG(two_bedroom_rent)::NUMERIC, 2) as avg_rent
            FROM rents
            WHERE two_bedroom_rent > 0
        """)
        min_rent, max_rent, avg_rent = cursor.fetchone()
        print(f"\n   2-Bedroom Rent Statistics:")
        print(f"     Min: ${min_rent:,}")
        print(f"     Max: ${max_rent:,}")
        print(f"     Avg: ${avg_rent:,}")

        # Commit transaction
        conn.commit()
        print("\n✅ Data loaded successfully!")

    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("FMR Data Loader")
    print("=" * 60)
    load_data()
    print("\n🎉 All done!")
    print("\nNext: Run exploratory analysis with Jupyter notebooks")
