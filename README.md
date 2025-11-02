# Housing Data Exploration

Exploring housing, homelessness, and inequality data across US geography and time.

## Overview

This project analyzes HUD Fair Market Rent (FMR) data to understand rental affordability across the United States. Using the HUD API, it fetches real-time data and generates insights about:

- **Rental price distributions** across different unit sizes
- **Geographic comparisons** identifying most/least expensive areas
- **Rent premium analysis** showing price differences between unit types
- **Statistical summaries** of national housing costs

## Quick Start

### 1. Get HUD API Access

1. Create a free account at https://www.huduser.gov/portal/dataset/fmr-api.html
2. Obtain your API access token
3. Add the token to `.env` file (see Configuration section below)

### 2. Install & Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run analysis
python3 explore_fmr.py
```

## Configuration

Create a `.env` file in the project root:

```bash
HUD_API_KEY=your_api_token_here
```

See `.env.example` for reference.

## What the Script Produces

**Console Output:**
- 2-bedroom rent statistics (min, max, average, median)
- Most and least expensive metro areas
- Top 10 areas with largest studio-to-3-bedroom rent differences

**Generated Files:**
- `fmr_data.json` - Complete dataset in JSON format (all 5,400+ areas)
- `two_bedroom_rent_histogram.png` - Distribution of 2-bedroom rents
- `studio_vs_two_bedroom_scatter.png` - Correlation between unit sizes

## Interactive Data Explorer

After running the script, open the interactive explorer in your browser:

```bash
# In a new terminal window, from the project directory:
python3 -m http.server 8000
```

Then visit: **http://localhost:8000**

The explorer lets you:
- Filter data by state
- Filter by area type (metro vs county)
- Search by area name
- Sort and paginate through all 5,400+ rental areas
- View real-time statistics
- Compare rental prices across different unit sizes

## Data Source

- **API**: HUD Fair Market Rents API
- **Coverage**: All US metropolitan areas and non-metropolitan counties
- **Data Year**: 2024 (configurable)
- **Update Frequency**: Annual

## Architecture

The project uses the HUD API instead of file downloads to:
- Eliminate file format/parsing issues
- Enable programmatic, real-time data access
- Support easy filtering by state or geography
- Maintain cleaner, simpler code

See `SETUP.md` for detailed setup and troubleshooting.
