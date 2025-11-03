-- Database schema for HUD Fair Market Rent Explorer
-- This creates the tables for storing FMR data from multiple sources

-- Drop existing tables if they exist (for fresh start)
DROP TABLE IF EXISTS rents CASCADE;
DROP TABLE IF EXISTS areas CASCADE;

-- Create areas table
CREATE TABLE areas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('metro', 'county')),
  state VARCHAR(2) NOT NULL,
  state_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on areas
CREATE INDEX idx_areas_state ON areas(state);
CREATE INDEX idx_areas_type ON areas(type);
CREATE INDEX idx_areas_name ON areas(name);

-- Create rents table
CREATE TABLE rents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  area_id UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  studio_rent INTEGER,
  one_bedroom_rent INTEGER,
  two_bedroom_rent INTEGER,
  three_bedroom_rent INTEGER,
  four_bedroom_rent INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(area_id)
);

-- Create indexes on rents
CREATE INDEX idx_rents_area_id ON rents(area_id);
CREATE INDEX idx_rents_two_bedroom ON rents(two_bedroom_rent);

-- Create a view for easy area + rent queries
CREATE VIEW areas_with_rents AS
SELECT
  a.id,
  a.name,
  a.type,
  a.state,
  a.state_name,
  COALESCE(r.studio_rent, 0) as studio_rent,
  COALESCE(r.one_bedroom_rent, 0) as one_bedroom_rent,
  COALESCE(r.two_bedroom_rent, 0) as two_bedroom_rent,
  COALESCE(r.three_bedroom_rent, 0) as three_bedroom_rent,
  COALESCE(r.four_bedroom_rent, 0) as four_bedroom_rent
FROM areas a
LEFT JOIN rents r ON a.id = r.area_id;

-- Create aggregation table (for pre-computed pivots)
CREATE TABLE aggregations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_by TEXT NOT NULL, -- comma-separated field names
  state VARCHAR(2),
  type VARCHAR(20),
  count INTEGER,
  avg_studio NUMERIC(10,2),
  avg_one_br NUMERIC(10,2),
  avg_two_br NUMERIC(10,2),
  avg_three_br NUMERIC(10,2),
  avg_four_br NUMERIC(10,2),
  min_two_br INTEGER,
  max_two_br INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_aggregations_state_type ON aggregations(state, type);

-- Useful queries for analysis
-- Get stats by state and type
CREATE VIEW pivot_by_state_type AS
SELECT
  a.state,
  a.type,
  COUNT(*) as count,
  ROUND(AVG(r.studio_rent)::NUMERIC, 2) as avg_studio,
  ROUND(AVG(r.one_bedroom_rent)::NUMERIC, 2) as avg_one_br,
  ROUND(AVG(r.two_bedroom_rent)::NUMERIC, 2) as avg_two_br,
  ROUND(AVG(r.three_bedroom_rent)::NUMERIC, 2) as avg_three_br,
  ROUND(AVG(r.four_bedroom_rent)::NUMERIC, 2) as avg_four_br,
  MIN(r.two_bedroom_rent) as min_two_br,
  MAX(r.two_bedroom_rent) as max_two_br
FROM areas a
LEFT JOIN rents r ON a.id = r.area_id
GROUP BY a.state, a.type
ORDER BY a.state, a.type;

-- Get overall statistics
CREATE VIEW overall_stats AS
SELECT
  COUNT(DISTINCT a.id) as total_areas,
  COUNT(DISTINCT CASE WHEN a.type = 'metro' THEN a.id END) as metro_count,
  COUNT(DISTINCT CASE WHEN a.type = 'county' THEN a.id END) as county_count,
  MIN(r.two_bedroom_rent) as min_two_br,
  MAX(r.two_bedroom_rent) as max_two_br,
  ROUND(AVG(r.two_bedroom_rent)::NUMERIC, 2) as avg_two_br,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.two_bedroom_rent) as median_two_br
FROM areas a
LEFT JOIN rents r ON a.id = r.area_id;
