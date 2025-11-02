#!/usr/bin/env python3
"""
HUD Fair Market Rent (FMR) Data Analysis Script

This script uses the HUD API to fetch Fair Market Rent data for 2024,
analyzes rental trends, and generates visualizations.

Requires HUD API access token (free account at https://www.huduser.gov/portal/dataset/fmr-api.html)
"""

import os
import json
from datetime import datetime
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up plotting style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# HUD API configuration
HUD_API_BASE = "https://www.huduser.gov/hudapi/public/fmr"
API_KEY = os.getenv("HUD_API_KEY")

def check_api_token():
    """
    Verify that the HUD API token is configured.

    Returns:
        bool: True if token exists, False otherwise
    """
    if not API_KEY:
        print("❌ Error: HUD_API_KEY not found in .env file")
        print("\nTo fix this:")
        print("1. Get your API token at: https://www.huduser.gov/portal/dataset/fmr-api.html")
        print("2. Create a .env file in the project root")
        print("3. Add: HUD_API_KEY=your_token_here")
        print("4. See .env.example for reference")
        return False
    return True

def get_api_headers():
    """
    Create HTTP headers for HUD API requests.

    Returns:
        dict: Headers with Bearer token authentication
    """
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

def fetch_fmr_data_for_state(state_code, year=2024):
    """
    Fetch FMR data for a specific state from the HUD API.

    Args:
        state_code (str): Two-letter state code (e.g., 'CA', 'NY')
        year (int): Fiscal year for data (default 2024)

    Returns:
        dict: API response data or None if request fails
    """
    url = f"{HUD_API_BASE}/statedata/{state_code}"
    params = {"year": year}

    try:
        response = requests.get(url, headers=get_api_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Extract the nested data structure
        return data.get("data") if isinstance(data, dict) else data
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Error fetching {state_code}: {e}")
        return None

def list_all_states():
    """
    Get list of all available states from HUD API.

    Returns:
        list: List of state dictionaries with state codes and names
    """
    url = f"{HUD_API_BASE}/listStates"

    try:
        response = requests.get(url, headers=get_api_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        # API returns data directly as a list, not wrapped in a dict
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("data", [])
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching state list: {e}")
        return []

def download_fmr_data():
    """
    Download FMR data for all states from HUD API.

    Returns:
        pandas.DataFrame: Combined FMR data for all states
    """
    print("📥 Fetching FMR data from HUD API...")
    print(f"API Endpoint: {HUD_API_BASE}/statedata")

    # Get list of states
    print("\n📍 Fetching state list...")
    states = list_all_states()

    if not states:
        print("❌ Failed to fetch state list")
        return None

    print(f"Found {len(states)} states/territories")

    # Collect all FMR data
    all_data = []

    print("\n📊 Fetching FMR data for each state...")
    for i, state in enumerate(states, 1):
        state_code = state.get("state_code", "")
        state_name = state.get("name", state_code)

        # Show progress every 5 states
        if i % 5 == 0:
            print(f"  [{i}/{len(states)}] Processing {state_name}...")

        # Fetch data for this state
        state_data = fetch_fmr_data_for_state(state_code)

        if state_data:
            # API returns nested structure with metroareas and counties
            if isinstance(state_data, dict):
                # Process metro areas
                if "metroareas" in state_data:
                    for area in state_data["metroareas"]:
                        all_data.append(area)

                # Process counties
                if "counties" in state_data:
                    for county in state_data["counties"]:
                        all_data.append(county)

    print(f"\n✅ Downloaded data for {len(all_data)} areas/counties")

    # Convert to DataFrame
    if not all_data:
        print("❌ No data retrieved")
        return None

    df = pd.DataFrame(all_data)
    return df

def clean_and_prepare_data(df):
    """
    Clean and prepare the FMR data for analysis.

    Args:
        df (pandas.DataFrame): Raw FMR data from API

    Returns:
        pandas.DataFrame: Cleaned data ready for analysis
    """
    print("\n🧹 Cleaning and preparing data...")

    # Display basic info about the dataset
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)[:10]}")

    # Identify and normalize rent columns
    # The API returns columns like "Efficiency", "One-Bedroom", "Two-Bedroom", etc.
    rent_column_map = {
        'Efficiency': 'studio_rent',
        'One-Bedroom': 'one_bedroom_rent',
        'Two-Bedroom': 'two_bedroom_rent',
        'Three-Bedroom': 'three_bedroom_rent',
        'Four-Bedroom': 'four_bedroom_rent',
    }

    # Convert rent columns to numeric
    for col in rent_column_map.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Rename columns for easier access
    df = df.rename(columns=rent_column_map)

    # Try to identify area name column (could be metro_name, county_name, or name)
    area_name_column = None
    for possible_col in ['metro_name', 'county_name', 'name']:
        if possible_col in df.columns:
            area_name_column = possible_col
            break

    if area_name_column and area_name_column != 'area_name':
        df = df.rename(columns={area_name_column: 'area_name'})

    print(f"✅ Cleaned dataset: {len(df)} records retained")
    return df

def export_to_json(df):
    """
    Export FMR data to JSON format for web explorer.

    Args:
        df (pandas.DataFrame): Cleaned FMR data
    """
    print("\n💾 Exporting data to JSON...")

    # Prepare the data structure
    areas = []

    for _, row in df.iterrows():
        # Determine area type and name
        area_type = "metro" if pd.notna(row.get("metro_name")) else "county"
        area_name = row.get("area_name", "Unknown")

        area_obj = {
            "name": area_name,
            "type": area_type,
            "state": row.get("statecode", ""),
            "state_name": row.get("statename", ""),
            "studio_rent": int(row["studio_rent"]) if pd.notna(row["studio_rent"]) else None,
            "one_bedroom_rent": int(row["one_bedroom_rent"]) if pd.notna(row["one_bedroom_rent"]) else None,
            "two_bedroom_rent": int(row["two_bedroom_rent"]) if pd.notna(row["two_bedroom_rent"]) else None,
            "three_bedroom_rent": int(row["three_bedroom_rent"]) if pd.notna(row["three_bedroom_rent"]) else None,
            "four_bedroom_rent": int(row["four_bedroom_rent"]) if pd.notna(row["four_bedroom_rent"]) else None,
        }
        areas.append(area_obj)

    # Create metadata
    two_br_rents = df["two_bedroom_rent"].dropna()
    two_br_rents = two_br_rents[two_br_rents > 0]

    metadata = {
        "year": 2024,
        "total_areas": len(areas),
        "fetched_date": datetime.now().isoformat(),
        "statistics": {
            "two_bedroom": {
                "min": int(two_br_rents.min()) if len(two_br_rents) > 0 else None,
                "max": int(two_br_rents.max()) if len(two_br_rents) > 0 else None,
                "average": int(two_br_rents.mean()) if len(two_br_rents) > 0 else None,
                "median": int(two_br_rents.median()) if len(two_br_rents) > 0 else None,
            }
        }
    }

    # Build final JSON structure
    export_data = {
        "metadata": metadata,
        "areas": areas
    }

    # Write to file
    output_file = "fmr_data.json"
    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"✅ Exported {len(areas)} areas to '{output_file}'")

def calculate_basic_statistics(df):
    """
    Calculate and display basic statistics about the FMR data.

    Args:
        df (pandas.DataFrame): Cleaned FMR data
    """
    print("\n📊 BASIC STATISTICS")
    print("=" * 50)

    # Total number of areas
    total_areas = len(df)
    print(f"Total number of areas: {total_areas:,}")

    # Focus on 2-bedroom rents since they're commonly referenced
    if 'two_bedroom_rent' in df.columns:
        two_br = df['two_bedroom_rent'].dropna()
        two_br = two_br[two_br > 0]  # Remove zero values

        print(f"\n2-Bedroom Rent Statistics:")
        print(f"  • Minimum: ${two_br.min():,.0f}")
        print(f"  • Maximum: ${two_br.max():,.0f}")
        print(f"  • Average: ${two_br.mean():,.0f}")
        print(f"  • Median: ${two_br.median():,.0f}")

        # Find most and least expensive areas
        if 'area_name' in df.columns:
            # Most expensive
            most_expensive_idx = df['two_bedroom_rent'].idxmax()
            most_expensive = df.loc[most_expensive_idx]
            print(f"\n🏆 Most expensive 2-bedroom area:")
            print(f"  • {most_expensive['area_name']}: ${most_expensive['two_bedroom_rent']:,.0f}")

            # Least expensive
            least_expensive_idx = df[df['two_bedroom_rent'] > 0]['two_bedroom_rent'].idxmin()
            least_expensive = df.loc[least_expensive_idx]
            print(f"\n💰 Least expensive 2-bedroom area:")
            print(f"  • {least_expensive['area_name']}: ${least_expensive['two_bedroom_rent']:,.0f}")

def create_rent_histogram(df):
    """
    Create a histogram showing the distribution of 2-bedroom rents.

    Args:
        df (pandas.DataFrame): FMR data with rent information
    """
    print("\n📈 Creating 2-bedroom rent histogram...")

    if 'two_bedroom_rent' not in df.columns:
        print("❌ Cannot create histogram: 2-bedroom rent data not found")
        return

    # Filter out missing values and zeros
    rent_data = df['two_bedroom_rent'].dropna()
    rent_data = rent_data[rent_data > 0]

    # Create the histogram
    plt.figure(figsize=(12, 6))
    plt.hist(rent_data, bins=50, alpha=0.7, color='skyblue', edgecolor='black')

    # Add labels and title
    plt.title('Distribution of 2-Bedroom Fair Market Rents (2024)', fontsize=16, fontweight='bold')
    plt.xlabel('Monthly Rent ($)', fontsize=12)
    plt.ylabel('Number of Areas', fontsize=12)

    # Add vertical lines for mean and median
    mean_rent = rent_data.mean()
    median_rent = rent_data.median()
    plt.axvline(mean_rent, color='red', linestyle='--', label=f'Mean: ${mean_rent:,.0f}')
    plt.axvline(median_rent, color='green', linestyle='--', label=f'Median: ${median_rent:,.0f}')

    # Format x-axis to show dollar signs
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    # Add legend and grid
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save the plot
    plt.savefig('two_bedroom_rent_histogram.png', dpi=300, bbox_inches='tight')
    print("✅ Histogram saved as 'two_bedroom_rent_histogram.png'")
    plt.close()

def create_studio_vs_two_bedroom_scatter(df):
    """
    Create a scatter plot comparing studio vs 2-bedroom rents.

    Args:
        df (pandas.DataFrame): FMR data with rent information
    """
    print("\n📈 Creating studio vs 2-bedroom rent scatter plot...")

    if 'studio_rent' not in df.columns or 'two_bedroom_rent' not in df.columns:
        print("❌ Cannot create scatter plot: Required rent data not found")
        return

    # Prepare data - remove rows with missing or zero values
    plot_data = df[['studio_rent', 'two_bedroom_rent']].dropna()
    plot_data = plot_data[(plot_data['studio_rent'] > 0) & (plot_data['two_bedroom_rent'] > 0)]

    # Create the scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(plot_data['studio_rent'], plot_data['two_bedroom_rent'],
                alpha=0.6, s=30, color='coral')

    # Add labels and title
    plt.title('Studio vs 2-Bedroom Fair Market Rents (2024)', fontsize=16, fontweight='bold')
    plt.xlabel('Studio Rent ($)', fontsize=12)
    plt.ylabel('2-Bedroom Rent ($)', fontsize=12)

    # Add a diagonal line
    max_val = max(plot_data['studio_rent'].max(), plot_data['two_bedroom_rent'].max())
    min_val = min(plot_data['studio_rent'].min(), plot_data['two_bedroom_rent'].min())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Equal Rent Line')

    # Format axes
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    # Add correlation coefficient
    correlation = plot_data['studio_rent'].corr(plot_data['two_bedroom_rent'])
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', transform=plt.gca().transAxes,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Add grid and legend
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    # Save the plot
    plt.savefig('studio_vs_two_bedroom_scatter.png', dpi=300, bbox_inches='tight')
    print("✅ Scatter plot saved as 'studio_vs_two_bedroom_scatter.png'")
    plt.close()

def find_largest_rent_differences(df):
    """
    Find areas with the biggest rent differences between unit sizes.

    Args:
        df (pandas.DataFrame): FMR data with rent information
    """
    print("\n🔍 Finding areas with largest studio to 3-bedroom rent differences...")

    if 'studio_rent' not in df.columns or 'three_bedroom_rent' not in df.columns:
        print("❌ Cannot calculate differences: Required rent data not found")
        return

    # Prepare analysis data
    analysis_cols = ['studio_rent', 'three_bedroom_rent']
    if 'area_name' in df.columns:
        analysis_cols.append('area_name')

    analysis_df = df[analysis_cols].copy()
    analysis_df = analysis_df.dropna()
    analysis_df = analysis_df[(analysis_df['studio_rent'] > 0) & (analysis_df['three_bedroom_rent'] > 0)]

    # Calculate differences
    analysis_df['rent_difference'] = analysis_df['three_bedroom_rent'] - analysis_df['studio_rent']
    analysis_df['rent_ratio'] = analysis_df['three_bedroom_rent'] / analysis_df['studio_rent']

    # Sort by absolute difference
    top_differences = analysis_df.nlargest(10, 'rent_difference')

    print("\n🏆 TOP 10 AREAS - Largest Studio to 3-Bedroom Rent Differences:")
    print("=" * 70)

    for i, (_, row) in enumerate(top_differences.iterrows(), 1):
        area_name = row.get('area_name', 'Unknown Area') if 'area_name' in row else 'Unknown Area'
        studio = row['studio_rent']
        three_br = row['three_bedroom_rent']
        difference = row['rent_difference']
        ratio = row['rent_ratio']

        print(f"{i:2d}. {area_name}")
        print(f"    Studio: ${studio:,.0f} → 3-BR: ${three_br:,.0f}")
        print(f"    Difference: ${difference:,.0f} (3-BR is {ratio:.1f}x studio)")
        print()

    # Additional summary statistics
    print(f"📊 Summary Statistics:")
    print(f"  • Average difference: ${analysis_df['rent_difference'].mean():,.0f}")
    print(f"  • Median difference: ${analysis_df['rent_difference'].median():,.0f}")
    print(f"  • Average ratio (3-BR/Studio): {analysis_df['rent_ratio'].mean():.1f}x")

def main():
    """
    Main function that orchestrates the entire analysis.
    """
    print("🏠 HUD Fair Market Rent Analysis")
    print("=" * 40)

    # Verify API token exists
    if not check_api_token():
        return

    # Step 1: Download the data
    df = download_fmr_data()
    if df is None:
        print("❌ Failed to download data. Exiting.")
        return

    # Step 2: Clean and prepare the data
    df_clean = clean_and_prepare_data(df)

    # Step 3: Export to JSON for web explorer
    export_to_json(df_clean)

    # Step 4: Calculate basic statistics
    calculate_basic_statistics(df_clean)

    # Step 5: Create visualizations
    create_rent_histogram(df_clean)
    create_studio_vs_two_bedroom_scatter(df_clean)

    # Step 6: Find largest rent differences
    find_largest_rent_differences(df_clean)

    print("\n✅ Analysis complete!")
    print("📊 Open 'index.html' in your browser to explore the data interactively.")

if __name__ == "__main__":
    main()
