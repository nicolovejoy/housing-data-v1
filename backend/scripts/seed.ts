/**
 * Database seed script - loads FMR data from fmr_data.json into PostgreSQL
 * Run with: npm run db:seed
 */

import fs from 'fs'
import path from 'path'

// Manual database connection for now
// In production, would use a proper ORM or connection pool

async function seed() {
  try {
    console.log('🌱 Starting database seed...')

    // Read fmr_data.json
    const dataPath = path.join(process.cwd(), 'fmr_data.json')
    if (!fs.existsSync(dataPath)) {
      console.error('❌ fmr_data.json not found!')
      console.error('   Run explore_fmr.py first to generate data')
      process.exit(1)
    }

    const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'))
    const areas = data.areas || []

    console.log(`📥 Loaded ${areas.length} areas from fmr_data.json`)

    // Instructions for manual loading
    console.log(`
✅ Data ready for loading!

To load data into PostgreSQL manually:

1. Start PostgreSQL:
   docker-compose up -d postgres

2. Wait for it to be ready (check: docker-compose ps)

3. Create database and tables:
   psql postgresql://postgres:postgres@localhost:5432 < backend/db/init.sql

4. For production loading, create a proper database client (see comments below)

Once PostgreSQL is running with the schema created, you can:
- Test the connection
- Verify row counts: SELECT COUNT(*) FROM areas;
- Run sample queries: SELECT * FROM pivot_by_state_type LIMIT 5;
    `)

    // Placeholder for future: proper database client setup
    console.log(`
📝 To implement automatic seeding:
   1. Install: npm install postgres
   2. Create connection in this file
   3. Loop through areas and insert into database
   4. Handle batch inserts for performance
    `)

  } catch (error) {
    console.error('❌ Seed failed:', error)
    process.exit(1)
  }
}

seed()
