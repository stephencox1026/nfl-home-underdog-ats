# Data Sources and Setup

## Current Issue

Spreadspoke.com only provides the current season (2025) data via direct CSV download. Historical data (2014-2024) is not available through the automated download.

## Solutions

### Option 1: Manual Download from Spreadspoke

1. Visit https://www.spreadspoke.com/data.html
2. Download historical CSV files for each year (if available)
3. Place them in a `data/` folder
4. Update `data_collector.py` to read from local files

### Option 2: Use nflfastR Data

nflfastR provides comprehensive historical NFL data. You can:

1. Install nflfastR data access:
   ```bash
   pip install nfl-data-py
   ```

2. Update `data_collector.py` to use nflfastR data instead

### Option 3: Use Current Season Data for Testing

The code will work with whatever data is available. Currently, it will analyze 2025 data if that's all that's available.

## Recommended Approach

For a complete analysis of 2014-2024, consider:

1. **Using nflfastR**: Most reliable and comprehensive
2. **Manual CSV download**: If Spreadspoke provides historical CSVs
3. **Hybrid approach**: Use nflfastR for game data, Spreadspoke for spreads (if available)

## Note

The code is designed to work with whatever data is available. If historical data isn't accessible, it will analyze whatever seasons are in the downloaded data.

