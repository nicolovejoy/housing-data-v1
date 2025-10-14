#!/usr/bin/env python3
"""
HUD Fair Market Rent (FMR) Data Analysis Script

This script downloads, analyzes, and visualizes HUD Fair Market Rent data for 2024.
It's designed to be beginner-friendly with extensive comments explaining each step.

Author: Generated for housing data analysis
Date: 2024
"""

# Import required libraries
import pandas as pd          # For data manipulation and analysis
import numpy as np           # For numerical operations
import matplotlib.pyplot as plt  # For creating plots and charts
import seaborn as sns        # For enhanced statistical visualizations
import requests             # For downloading data from URLs
from io import StringIO, BytesIO  # For handling string and binary data as file-like objects

# Set up plotting style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def download_fmr_data(url):
    """
    Download FMR data from HUD website.
    
    Args:
        url (str): The URL to download the Excel data from
    
    Returns:
        pandas.DataFrame: The downloaded data as a DataFrame
    """
    print("📥 Downloading HUD Fair Market Rent data...")
    print(f"Source: {url}")
    
    try:
        # Send HTTP request to download the Excel file
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Convert the downloaded Excel data to a pandas DataFrame
        # Use BytesIO to handle binary Excel data
        df = pd.read_excel(BytesIO(response.content))
        
        print(f"✅ Successfully downloaded {len(df)} records")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading data: {e}")
        return None
    except pd.errors.EmptyDataError:
        print("❌ Error: Downloaded file appears to be empty")
        return None
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None

def clean_and_prepare_data(df):
    """
    Clean and prepare the FMR data for analysis.
    
    Args:
        df (pandas.DataFrame): Raw FMR data
    
    Returns:
        pandas.DataFrame: Cleaned data ready for analysis
    """
    print("\n🧹 Cleaning and preparing data...")
    
    # Display basic info about the dataset
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Convert rent columns to numeric, handling any non-numeric values
    rent_columns = ['fmr_0', 'fmr_1', 'fmr_2', 'fmr_3', 'fmr_4']
    
    for col in rent_columns:
        if col in df.columns:
            # Convert to numeric, setting errors='coerce' to handle invalid values
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove rows where all rent values are missing
    df_clean = df.dropna(subset=rent_columns, how='all')
    
    # Create meaningful column names for easier reference
    if 'fmr_0' in df.columns:
        df_clean = df_clean.rename(columns={
            'fmr_0': 'studio_rent',
            'fmr_1': 'one_bedroom_rent', 
            'fmr_2': 'two_bedroom_rent',
            'fmr_3': 'three_bedroom_rent',
            'fmr_4': 'four_bedroom_rent'
        })
    
    print(f"✅ Cleaned dataset: {len(df_clean)} records retained")
    return df_clean

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
        
        print(f"\n2-Bedroom Rent Statistics:")
        print(f"  • Minimum: ${two_br.min():,.0f}")
        print(f"  • Maximum: ${two_br.max():,.0f}")
        print(f"  • Average: ${two_br.mean():,.0f}")
        print(f"  • Median: ${two_br.median():,.0f}")
        
        # Find most and least expensive metro areas
        if 'areaname' in df.columns:
            # Most expensive
            most_expensive = df.loc[df['two_bedroom_rent'].idxmax()]
            print(f"\n🏆 Most expensive 2-bedroom area:")
            print(f"  • {most_expensive['areaname']}: ${most_expensive['two_bedroom_rent']:,.0f}")
            
            # Least expensive (excluding zero values)
            non_zero_rents = df[df['two_bedroom_rent'] > 0]
            if not non_zero_rents.empty:
                least_expensive = non_zero_rents.loc[non_zero_rents['two_bedroom_rent'].idxmin()]
                print(f"\n💰 Least expensive 2-bedroom area:")
                print(f"  • {least_expensive['areaname']}: ${least_expensive['two_bedroom_rent']:,.0f}")

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
    
    # Filter out missing values and outliers for better visualization
    rent_data = df['two_bedroom_rent'].dropna()
    rent_data = rent_data[rent_data > 0]  # Remove zero values
    
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
    
    # Show the plot
    plt.show()

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
    
    # Prepare data - remove rows with missing values in either column
    plot_data = df[['studio_rent', 'two_bedroom_rent']].dropna()
    # Remove zero values for better visualization
    plot_data = plot_data[(plot_data['studio_rent'] > 0) & (plot_data['two_bedroom_rent'] > 0)]
    
    # Create the scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(plot_data['studio_rent'], plot_data['two_bedroom_rent'], 
                alpha=0.6, s=30, color='coral')
    
    # Add labels and title
    plt.title('Studio vs 2-Bedroom Fair Market Rents (2024)', fontsize=16, fontweight='bold')
    plt.xlabel('Studio Rent ($)', fontsize=12)
    plt.ylabel('2-Bedroom Rent ($)', fontsize=12)
    
    # Add a diagonal line to show where studio = 2-bedroom
    max_val = max(plot_data['studio_rent'].max(), plot_data['two_bedroom_rent'].max())
    min_val = min(plot_data['studio_rent'].min(), plot_data['two_bedroom_rent'].min())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Equal Rent Line')
    
    # Format axes to show dollar signs
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
    
    # Show the plot
    plt.show()

def find_largest_rent_differences(df):
    """
    Find areas with the biggest rent differences between studio and 3-bedroom units.
    
    Args:
        df (pandas.DataFrame): FMR data with rent information
    """
    print("\n🔍 Finding areas with largest studio to 3-bedroom rent differences...")
    
    if 'studio_rent' not in df.columns or 'three_bedroom_rent' not in df.columns:
        print("❌ Cannot calculate differences: Required rent data not found")
        return
    
    # Calculate rent differences
    analysis_df = df.copy()
    analysis_df = analysis_df.dropna(subset=['studio_rent', 'three_bedroom_rent'])
    analysis_df = analysis_df[(analysis_df['studio_rent'] > 0) & (analysis_df['three_bedroom_rent'] > 0)]
    
    # Calculate absolute and percentage differences
    analysis_df['rent_difference'] = analysis_df['three_bedroom_rent'] - analysis_df['studio_rent']
    analysis_df['rent_ratio'] = analysis_df['three_bedroom_rent'] / analysis_df['studio_rent']
    
    # Sort by absolute difference (largest first)
    top_differences = analysis_df.nlargest(10, 'rent_difference')
    
    print("\n🏆 TOP 10 AREAS - Largest Studio to 3-Bedroom Rent Differences:")
    print("=" * 70)
    
    for i, (_, row) in enumerate(top_differences.iterrows(), 1):
        area_name = row.get('areaname', 'Unknown Area')
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
    
    # URL for HUD FMR data (Excel format)
    fmr_url = "https://www.huduser.gov/portal/datasets/fmr/fmr2024/FY24_FMRs.xlsx"
    
    # Step 1: Download the data
    df = download_fmr_data(fmr_url)
    if df is None:
        print("❌ Failed to download data. Exiting.")
        return
    
    # Step 2: Clean and prepare the data
    df_clean = clean_and_prepare_data(df)
    
    # Step 3: Calculate basic statistics
    calculate_basic_statistics(df_clean)
    
    # Step 4: Create visualizations
    create_rent_histogram(df_clean)
    create_studio_vs_two_bedroom_scatter(df_clean)
    
    # Step 5: Find largest rent differences
    find_largest_rent_differences(df_clean)
    
    print("\n✅ Analysis complete! Check the generated PNG files for visualizations.")

# This is the standard Python idiom for running code when the script is executed directly
# (as opposed to being imported as a module)
if __name__ == "__main__":
    main()