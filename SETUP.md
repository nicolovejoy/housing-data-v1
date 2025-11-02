# Setup Guide

## Prerequisites

- Python 3.7+
- HUD API access token (free account required)

## Step 1: Get Your HUD API Token

1. Visit https://www.huduser.gov/portal/dataset/fmr-api.html
2. Click "Create Account" or sign in if you already have an account
3. Complete the registration process
4. Once logged in, your API token will be displayed on the API page
5. Copy your API token

## Step 2: Configure Your Local Environment

Create a `.env` file in the project root directory:

```bash
# .env file
HUD_API_KEY=your_actual_api_token_here
```

**Important:**
- Never commit `.env` to version control (it's listed in `.gitignore`)
- Keep your API token private
- You can reference `.env.example` for the format

## Step 3: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

## Step 4: Run the Analysis

```bash
python3 explore_fmr.py
```

The script will:
1. Read your HUD API token from `.env`
2. Fetch FMR data for all states for 2024
3. Analyze and aggregate the data
4. Generate statistics and visualizations
5. Create PNG files with charts

## Troubleshooting

### "HUD_API_KEY not found" Error

Make sure:
- `.env` file exists in the project root
- Contains `HUD_API_KEY=your_token_here`
- The token is correct (copy from HUD website again if needed)

### API Connection Errors

- Check your internet connection
- Verify the API token is valid at https://www.huduser.gov/portal/dataset/fmr-api.html
- HUD API may be temporarily unavailable (check their status page)

### Missing Dependencies

If you see import errors:
```bash
pip install -r requirements.txt
```

## What Happens When You Run It

**Fetches Data:**
- Queries HUD API for state-level FMR data
- Retrieves rent data for all bedroom counts (studio through 4-bedroom)
- Aggregates national statistics

**Generates Reports:**
- Console output with statistics
- PNG visualization files in the project directory

**Expected Runtime:**
- First run: ~30-60 seconds (API calls + processing)
- Data file: ~50-100 states × multiple bedroom counts

## Future Extensions

Once the basic script runs successfully, you could:
- Filter by specific states
- Compare year-over-year changes
- Analyze affordability relative to income data
- Create interactive dashboards
- Export data to CSV/Excel

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `HUD_API_KEY` | Your HUD API access token | Yes | `abc123xyz...` |

## Getting Help

- HUD API Documentation: https://www.huduser.gov/portal/dataset/fmr-api.html
- Project Issues: Create an issue on the GitHub repository
