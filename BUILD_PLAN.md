# Housing Data Explorer - Build Plan

## Overview
Migrate from static HTML explorer to full-stack Next.js + PostgreSQL + Railway application with interactive pivot tables and drill-down exploration.

**Final Architecture:**
- Frontend: Next.js 15 (TypeScript, Tailwind CSS)
- Backend: Next.js API Routes (Node.js)
- Database: PostgreSQL on Railway
- Infrastructure: Terraform for Railway config
- Deployment: Git push to Railway

**Timeline:** 8 phases with validation checkpoints

---

## Phase 1: Repository Restructure
**Goal:** Reorganize project into frontend/backend/infrastructure structure

**Tasks:**
- Create `frontend/`, `backend/`, `infrastructure/`, `shared/` directories
- Move existing `index.html` to `frontend/public/` (archive)
- Create `shared/types.ts` for shared TypeScript types
- Set up `.env.example` for both frontend and backend
- Update `.gitignore` for Next.js (node_modules, .next, dist)

**Checkpoint 1A: Folder Structure**
```bash
ls -la housing-data-v1/
# Should show: frontend/, backend/, infrastructure/, shared/, explore_fmr.py, etc.
```

**Validation:**
- [ ] frontend/ directory exists with placeholder files
- [ ] backend/ directory exists with placeholder files
- [ ] infrastructure/ directory exists
- [ ] shared/ directory exists with types.ts stub
- [ ] Old files still intact (explore_fmr.py, fmr_data.json generation works)

---

## Phase 2: Next.js Setup & Local Development Environment
**Goal:** Get Next.js running locally with TypeScript and Tailwind

**Tasks:**
- Create Next.js app in `/` root (monorepo approach)
- Configure TypeScript (tsconfig.json)
- Set up Tailwind CSS
- Create basic app structure:
  - `app/layout.tsx` (main layout)
  - `app/page.tsx` (home/explorer page)
  - `components/` structure
  - `lib/` utilities
- Create `.env.local` for local API calls
- Set up docker-compose.yml for local PostgreSQL

**Checkpoint 2A: Next.js Running Locally**
```bash
cd housing-data-v1
npm run dev
# Should start: "Local: http://localhost:3000"
```

**Validation:**
- [ ] `npm run dev` starts without errors
- [ ] Browser shows Next.js welcome page or custom home page
- [ ] `app/` directory structure exists
- [ ] TypeScript compiles with no errors
- [ ] Tailwind CSS is loaded (inspect page for tailwind classes)

**Checkpoint 2B: Docker Compose for Local Postgres**
```bash
docker-compose up -d
# Should start PostgreSQL on localhost:5432
```

**Validation:**
- [ ] PostgreSQL container starts
- [ ] Can connect with: `psql postgresql://user:password@localhost:5432/fmr_data`
- [ ] Empty database exists
- [ ] Connection string works in `.env.local`

---

## Phase 3: Database Schema & Data Loading
**Goal:** Design PostgreSQL schema and load FMR data

**Tasks:**
- Design schema in `backend/db/schema.ts`:
  - `areas` table (id, name, state, type, created_at)
  - `rents` table (area_id, studio, one_br, two_br, three_br, four_br)
  - `aggregations` table (for pre-computed pivot data)
- Create migration script `backend/scripts/load-fmr-data.ts`
- Load existing `fmr_data.json` into PostgreSQL
- Verify data integrity (row counts, rent ranges)

**Checkpoint 3A: Schema Created**
```bash
npm run db:migrate
# Should create tables without errors
```

**Validation:**
- [ ] `psql` shows tables: `areas`, `rents`, `aggregations`
- [ ] Tables have correct columns
- [ ] No errors in `postgres` logs

**Checkpoint 3B: Data Loaded & Verified**
```bash
npm run db:seed
# Should load data from fmr_data.json
```

**Validation:**
- [ ] `SELECT COUNT(*) FROM areas;` returns 5449
- [ ] `SELECT COUNT(*) FROM rents;` returns 5449
- [ ] `SELECT MIN(two_br), MAX(two_br) FROM rents;` returns $473, $4054
- [ ] No NULL values in critical columns
- [ ] State breakdown looks correct (50 states + PR/VI/etc.)

**Checkpoint 3C: Data Queries Work**
```bash
# Run test queries manually:
SELECT state, COUNT(*) as count FROM areas GROUP BY state ORDER BY count DESC;
SELECT type, COUNT(*) as count FROM areas GROUP BY type;
```

**Validation:**
- [ ] Queries execute without errors
- [ ] Results match expectations (CA, TX, NY have most areas)
- [ ] Type breakdown shows both metros and counties

---

## Phase 4: API Routes (Backend)
**Goal:** Build Next.js API routes for pivot and drill-down

**Tasks:**
- Create `app/api/pivot/route.ts`:
  - Query: `SELECT state, type, COUNT(*), AVG(two_br) FROM areas JOIN rents...`
  - Returns: aggregated data structure
- Create `app/api/drilldown/route.ts`:
  - Query by state/type filters
  - Returns: detailed area records
- Create `app/api/stats/route.ts`:
  - Overall statistics
  - Returns: min/max/avg for all rent types
- Add error handling and logging

**Checkpoint 4A: Endpoints Respond**
```bash
curl http://localhost:3000/api/stats
# Should return JSON with statistics

curl http://localhost:3000/api/pivot?group_by=state
# Should return aggregated pivot data

curl http://localhost:3000/api/drilldown?state=CA&type=metro
# Should return detailed area records
```

**Validation:**
- [ ] All endpoints return 200 status
- [ ] Responses are valid JSON
- [ ] Data structure matches expected format
- [ ] Queries execute in < 1 second
- [ ] No database errors in logs

**Checkpoint 4B: Response Data Validation**
```bash
# Verify pivot response structure:
# { "state": "CA", "type": "metro", "count": 30, "avg_rent": 2200 }

# Verify drilldown response:
# { "name": "San Francisco...", "type": "metro", "studio_rent": 2292, ... }

# Verify stats response:
# { "two_bedroom": { "min": 473, "max": 4054, "avg": 1214, "median": 1068 } }
```

**Validation:**
- [ ] Pivot data aggregates correctly
- [ ] Drilldown returns proper area details
- [ ] Stats match what Python script generates
- [ ] No missing or malformed fields

---

## Phase 5: React Components & UI
**Goal:** Build interactive data explorer frontend

**Tasks:**
- Create `components/PivotTable.tsx`:
  - Displays aggregated data as interactive table
  - Click row to drill down
  - Sort/filter controls
- Create `components/DrillDown.tsx`:
  - Shows detailed areas for selected group
  - Back button to pivot view
  - Search/filter on name
- Create `components/StatsDashboard.tsx`:
  - Display overall stats
  - Show min/max/avg rents
- Create `components/DataExplorer.tsx`:
  - Main container component
  - State management with hooks
  - Loading/error states
- Create `lib/api.ts`:
  - Fetch functions for pivot, drilldown, stats
  - Error handling

**Checkpoint 5A: Components Render**
```bash
npm run dev
# Navigate to home page
# Should see PivotTable, StatsDashboard, no errors in console
```

**Validation:**
- [ ] No TypeScript errors
- [ ] All components render without crashing
- [ ] API calls start (check Network tab)
- [ ] Loading states appear briefly
- [ ] Console has no errors

**Checkpoint 5B: User Interactions Work**
```
Manual testing:
1. Load home page → stats display
2. View pivot table → shows state/type/count/avg
3. Click state row → drills down to show areas in that state
4. Click back → returns to pivot view
5. Search by name → filters results
```

**Validation:**
- [ ] Pivot table displays correctly
- [ ] Drill-down navigation works
- [ ] Back button functional
- [ ] Search filters results in real-time
- [ ] Data updates when filters change
- [ ] No console errors
- [ ] Page is responsive (check mobile view)

---

## Phase 6: Styling & Polish
**Goal:** Match notemaxxing design patterns, ensure UX is polished

**Tasks:**
- Apply Tailwind classes matching notemaxxing style
- Create shared UI components (`Button`, `Card`, `Table`, etc.)
- Add dark mode support (optional)
- Add loading skeletons
- Add error boundaries
- Improve mobile responsiveness
- Add hover/interaction states

**Checkpoint 6A: Visual Design Complete**
```
Manual review:
- Colors consistent across app
- Typography is clean and readable
- Spacing follows design system
- Tables are responsive
- Buttons have proper hover states
```

**Validation:**
- [ ] Design matches notemaxxing aesthetic
- [ ] All text is readable
- [ ] Color contrast passes accessibility check
- [ ] Mobile view is usable
- [ ] No layout shifts when loading

---

## Phase 7: Terraform & Infrastructure Setup
**Goal:** Define Railway infrastructure as code

**Tasks:**
- Create `infrastructure/main.tf`:
  - Define Railway PostgreSQL service
  - Define Railway Node.js service
  - Set environment variables
  - Configure secrets (API keys)
- Create `infrastructure/variables.tf`:
  - Input variables for deployment
- Create `railway.json`:
  - Railway service configuration
  - Build/start commands
- Create `.env.example`:
  - Document all required env vars

**Checkpoint 7A: Terraform Validates**
```bash
cd infrastructure
terraform init
terraform validate
# Should show no errors
```

**Validation:**
- [ ] `terraform validate` passes
- [ ] All variables defined
- [ ] No syntax errors in TF files
- [ ] railway.json is valid JSON

**Checkpoint 7B: Local Terraform Plan**
```bash
terraform plan
# Should show resources that will be created (in dry-run mode)
```

**Validation:**
- [ ] Plan shows PostgreSQL service
- [ ] Plan shows Node.js app service
- [ ] No errors in plan output
- [ ] Resource names match expected pattern

---

## Phase 8: Deployment to Railway
**Goal:** Deploy to Railway and verify production environment

**Tasks:**
- Connect Railway to GitHub repo
- Set environment variables in Railway dashboard
- Trigger deployment via git push
- Monitor deployment logs
- Run production validation tests
- Verify data is accessible
- Test API endpoints on production URL

**Checkpoint 8A: Deployment Successful**
```
In Railway dashboard:
- Deployment shows "Success"
- PostgreSQL service is "Running"
- Node.js app is "Running"
- View logs show no errors
```

**Validation:**
- [ ] Railway dashboard shows green status
- [ ] No error logs in build phase
- [ ] App starts without crashing
- [ ] Database connection successful
- [ ] Deployment URL is accessible

**Checkpoint 8B: Production Data & APIs Work**
```bash
# From production URL (e.g., https://housing-data-prod.railway.app)
curl https://your-railway-url/api/stats
curl https://your-railway-url/api/pivot?group_by=state
curl https://your-railway-url/api/drilldown?state=CA
```

**Validation:**
- [ ] API endpoints respond with 200 status
- [ ] Data matches local development
- [ ] Response times are acceptable (< 2s)
- [ ] No database errors
- [ ] Frontend loads and communicates with production backend

**Checkpoint 8C: End-to-End User Flow**
```
Production testing:
1. Load https://your-railway-url
2. Stats display correctly
3. Pivot table shows all states
4. Click to drill down to specific state
5. See detailed area list
6. Search for area by name
7. No console errors
8. Mobile view works
```

**Validation:**
- [ ] All user flows work in production
- [ ] Data is accurate
- [ ] Performance is acceptable
- [ ] No errors or timeouts

---

## Rollback Plan

If any phase fails at checkpoint:

1. **Phase 1-2 (Structure/Next.js):** Delete new files, keep original
2. **Phase 3 (Database):** Drop PostgreSQL database, re-create
3. **Phase 4-5 (API/Components):** Revert git commits, fix code
4. **Phase 6 (Styling):** Revert CSS changes
5. **Phase 7 (Terraform):** Don't apply, fix TF and re-plan
6. **Phase 8 (Railway):** Rollback to previous version in Railway dashboard

---

## Success Criteria (Final)

✅ User can access interactive data explorer at production URL
✅ Pivot table shows aggregated data by state/type
✅ Drill-down shows detailed areas for selected group
✅ Search/filter works in real-time
✅ All APIs respond in < 2 seconds
✅ No console errors in production
✅ Mobile view is functional
✅ Data matches original Python analysis
✅ PostgreSQL has all 5,449 areas loaded
✅ Terraform manages all infrastructure

---

## Updated Approach: Jupyter-First Exploration

**New Strategy:**
After completing Phase 3 (database ready), pause the Next.js/Railway build and switch to **Jupyter notebooks** for:
- Deep exploratory data analysis
- Testing pivot table logic and aggregations
- Understanding data relationships
- Preparing for multi-dataset integration

**Why this order:**
1. Phases 1-3 give us a working database with FMR data
2. Jupyter lets us explore and test queries interactively
3. We can add other API data sources (Census, income data, etc.) via Jupyter
4. Once we understand the data relationships, we build a better Next.js UI
5. Database is already set up for production deployment later

**Multi-Dataset Integration Plan:**
- Phase 3: FMR data loaded in PostgreSQL
- Jupyter Phase: Add Census data, income data, cost-of-living indices
- Create normalized schema for multi-source data
- Build aggregations that combine datasets
- Then return to Next.js UI with fully integrated dataset

## Timeline Estimate (Updated)

| Phase | Tasks | Est. Time | Status |
|-------|-------|-----------|--------|
| 1 | Restructure | 30 min | ✅ Complete |
| 2 | Next.js setup | 1 hour | ✅ Complete |
| 3a | Database schema | 30 min | ✅ Complete |
| 3b | Load FMR data | 15 min | 🔄 In progress |
| 3c | Verify data | 5 min | ⏭️ Next |
| **Jupyter Exploration** | Multi-dataset integration | 2-3 hours | ⏭️ After data loaded |
| 4-8 | React UI & Deployment | 5-6 hours | ⏳ Later (after Jupyter) |
| **Total to Jupyter Ready** | | **~2.5 hours** | 🔄 Now |
| **Total Full Project** | | **~9-10 hours** | |

---

## Commands Reference

```bash
# Phase 2: Start dev server
npm run dev

# Phase 3: Database operations
npm run db:migrate      # Create tables
npm run db:seed         # Load data from fmr_data.json

# Phase 4: Test APIs locally
curl http://localhost:3000/api/stats
curl http://localhost:3000/api/pivot
curl http://localhost:3000/api/drilldown

# Phase 7: Terraform
cd infrastructure
terraform init
terraform plan
terraform apply

# Phase 8: Deploy
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

---

## Potential Data Sources for Integration

During Jupyter exploration phase, consider adding:

### Income & Affordability Data
- **Census Bureau API** - Median household income by area
- **HUD Income Limits API** - Income thresholds for housing programs
- **BLS (Bureau of Labor Statistics)** - Cost of living indices

### Housing Market Data
- **Zillow API** - Current market rent data
- **NOAA/Census** - Population and demographic data
- **Google Trends** - Housing search interest by area

### Geographic & Administrative Data
- **US Census Geocoding API** - Lat/long for metro areas
- **USGS** - Geographic boundaries and shapefiles

### Implementation Pattern (Jupyter):
1. Create Python functions for each API
2. Test data normalization and schema fit
3. Load into PostgreSQL alongside FMR data
4. Create SQL views that combine datasets
5. Document relationships in schema diagrams
6. Then build React UI around combined data

---

## Notes

- Keep original `explore_fmr.py` script for data re-generation
- Python script still outputs `fmr_data.json` for backup
- Database is source of truth once loaded
- Can re-run Python script to update data in DB anytime
- Frontend/Backend can be updated independently
- Jupyter notebooks will live in `/notebooks/` directory
- Each API integration gets its own notebook for testing
