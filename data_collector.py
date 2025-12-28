"""
Data collection module for NFL game data, spreads, weather, QBs, and coaches.
Primary source: nflfastR (nfl-data-py)
Fallback: Spreadspoke.com
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, List, Optional
import config
import utils
from datetime import datetime
import logging
from team_mappings import get_team_name_from_abbrev

try:
    import nfl_data_py as nfl
    HAS_NFL_DATA = True
except ImportError:
    HAS_NFL_DATA = False
    logging.warning("nfl-data-py not installed. Install with: pip install nfl-data-py")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_nflfastr_data() -> pd.DataFrame:
    """
    Download NFL data from nflfastR (nfl-data-py).
    This is the primary data source for historical data.
    
    Returns:
        DataFrame with NFL game data including schedules, spreads, weather, QBs
    """
    if not HAS_NFL_DATA:
        logger.error("nfl-data-py is not installed. Install with: pip install nfl-data-py")
        return pd.DataFrame()
    
    logger.info("Downloading NFL data from nflfastR...")
    
    years = list(range(config.START_SEASON, config.END_SEASON + 1))
    logger.info(f"Downloading data for years: {years}")
    
    try:
        # Import schedules which includes spreads, weather, QBs, and game results
        df = nfl.import_schedules(years)
        
        if df.empty:
            logger.warning("No data returned from nflfastR")
            return pd.DataFrame()
        
        logger.info(f"Successfully downloaded {len(df)} games from nflfastR")
        return df
        
    except Exception as e:
        logger.error(f"Error downloading from nflfastR: {e}")
        return pd.DataFrame()


def download_spreadspoke_data() -> pd.DataFrame:
    """
    Download NFL data from Spreadspoke.com CSV.
    Tries to download data for multiple years and combines them.
    
    Returns:
        DataFrame with NFL game data
    """
    logger.info("Downloading NFL data from Spreadspoke...")
    
    all_dataframes = []
    
    # Try to download data for each year in our range
    for year in range(config.START_SEASON, config.END_SEASON + 1):
        url = f"https://www.spreadspoke.com/data/nfl_{year}.csv"
        try:
            logger.info(f"Attempting to download data for {year}...")
            df = pd.read_csv(url, timeout=30)
            if len(df) > 0:
                all_dataframes.append(df)
                logger.info(f"Downloaded {len(df)} games for {year}")
        except Exception as e:
            logger.debug(f"Could not download data for {year}: {e}")
            continue
    
    # If we got some data, combine it
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        logger.info(f"Successfully downloaded {len(combined_df)} total games from Spreadspoke")
        return combined_df
    
    # Fallback: try the main 2025 file (might have some historical data)
    try:
        logger.info("Trying main NFL data file...")
        response = requests.get(config.SPREADSPOKE_CSV_URL, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(config.SPREADSPOKE_CSV_URL)
        logger.info(f"Downloaded {len(df)} games from main file")
        return df
    except Exception as e:
        logger.warning(f"Could not download from main URL: {e}")
    
    # Final fallback: try to scrape the data page
    try:
        logger.info("Attempting to scrape from Spreadspoke website...")
        response = requests.get(config.SPREADSPOKE_DATA_URL, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for CSV download link
        csv_link = None
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'nfl_2025.csv' in href or ('nfl.csv' in href and 'playoff' not in href and 'superbowl' not in href):
                csv_link = href
                break
        
        if csv_link:
            if not csv_link.startswith('http'):
                csv_link = 'https://www.spreadspoke.com' + csv_link
            df = pd.read_csv(csv_link)
            logger.info(f"Successfully downloaded {len(df)} games from Spreadspoke")
            return df
    except Exception as e2:
        logger.error(f"Failed to scrape Spreadspoke: {e2}")
    
    # If all else fails, return empty DataFrame
    logger.error("Could not download Spreadspoke data. Please download manually from https://www.spreadspoke.com/data.html")
    return pd.DataFrame()


def fetch_qb_data(game_date: datetime, team: str) -> Optional[str]:
    """
    Fetch starting quarterback for a team on a specific date.
    This is a placeholder - in practice, you'd need to scrape or use an API.
    
    Args:
        game_date: Date of the game
        team: Team name
        season: Season year
        
    Returns:
        Quarterback name or None
    """
    # TODO: Implement actual QB data fetching
    # Options:
    # 1. Scrape from Pro-Football-Reference.com
    # 2. Use NFL API if available
    # 3. Use a sports data API
    # 4. Manual data entry for key games
    
    # For now, return None - this will need to be implemented
    return None


def fetch_coach_data(game_date: datetime, team: str) -> Optional[str]:
    """
    Fetch head coach for a team on a specific date.
    This is a placeholder - in practice, you'd need to scrape or use an API.
    
    Args:
        game_date: Date of the game
        team: Team name
        
    Returns:
        Head coach name or None
    """
    # TODO: Implement actual coach data fetching
    # Options:
    # 1. Scrape from Pro-Football-Reference.com
    # 2. Use NFL API if available
    # 3. Manual data entry for key games
    
    # For now, return None - this will need to be implemented
    return None


def enrich_game_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich game data with additional information.
    Handles both nflfastR and Spreadspoke data formats.
    
    Args:
        df: DataFrame with game data (from nflfastR or Spreadspoke)
        
    Returns:
        Enriched DataFrame
    """
    logger.info("Enriching game data...")
    
    # Handle team names - nflfastR uses abbreviations, Spreadspoke uses full names
    if 'home_team' in df.columns and 'team_home' not in df.columns:
        # nflfastR format - convert abbreviations to full names
        df['home_team_normalized'] = df['home_team'].apply(get_team_name_from_abbrev)
        df['away_team_normalized'] = df['away_team'].apply(get_team_name_from_abbrev)
    elif 'team_home' in df.columns:
        # Spreadspoke format - already full names, just normalize
        df['home_team_normalized'] = df['team_home'].apply(utils.normalize_team_name)
        df['away_team_normalized'] = df['team_away'].apply(utils.normalize_team_name)
    else:
        logger.warning("Could not find team name columns")
        df['home_team_normalized'] = None
        df['away_team_normalized'] = None
    
    # Parse dates - nflfastR uses 'gameday', Spreadspoke uses 'schedule_date'
    date_col = None
    for col in ['gameday', 'schedule_date', 'date', 'game_date', 'Date']:
        if col in df.columns:
            date_col = col
            break
    
    if date_col:
        if date_col == 'gameday':
            # nflfastR format - already in YYYY-MM-DD format
            df['game_date'] = pd.to_datetime(df[date_col], errors='coerce')
        else:
            df['game_date'] = df[date_col].apply(utils.parse_date)
        
        # Use season column if available (both sources have it)
        if 'season' in df.columns:
            df['season'] = df['season']
        elif 'schedule_season' in df.columns:
            df['season'] = df['schedule_season']
        else:
            df['season'], _ = zip(*df['game_date'].apply(
                lambda x: utils.get_season_week(x) if x else (None, None)
            ))
        
        # Use week column if available
        if 'week' in df.columns:
            df['week'] = df['week']
        elif 'schedule_week' in df.columns:
            df['week'] = df['schedule_week']
        else:
            _, df['week'] = zip(*df['game_date'].apply(
                lambda x: utils.get_season_week(x) if x else (None, None)
            ))
    else:
        logger.warning("Could not find date column in data")
        df['game_date'] = None
        df['season'] = None
        df['week'] = None
    
    # Add month
    df['month'] = df['game_date'].apply(lambda x: x.month if x else None)
    
    # Check if teams are in same division
    # nflfastR has 'div_game' column (1 = divisional, 0 = not)
    if 'div_game' in df.columns:
        df['is_divisional'] = df['div_game'] == 1
    elif 'home_team_normalized' in df.columns and 'away_team_normalized' in df.columns:
        df['is_divisional'] = df.apply(
            lambda row: utils.are_same_division(
                row['home_team_normalized'], 
                row['away_team_normalized']
            ), axis=1
        )
    else:
        df['is_divisional'] = False
    
    # Calculate spread from home team perspective
    # nflfastR has 'spread_line' which is from home perspective (negative = home favorite)
    # Spreadspoke has 'spread_favorite' which needs conversion
    if 'spread_line' in df.columns:
        # nflfastR format - already from home perspective
        df['home_spread'] = df['spread_line'].apply(utils.safe_float)
        # Convert to our convention: positive = home underdog
        df['home_spread'] = -df['home_spread']  # Flip sign so positive = home underdog
    else:
        # Spreadspoke format - need to determine favorite
        spread_col = None
        for col in ['spread_favorite', 'spread', 'line', 'point_spread']:
            if col in df.columns:
                spread_col = col
                break
        
        if spread_col:
            favorite_col = None
            for col in ['team_favorite_id', 'favorite', 'team_favorite']:
                if col in df.columns:
                    favorite_col = col
                    break
            
            if favorite_col:
                def calculate_home_spread(row):
                    spread = utils.safe_float(row[spread_col])
                    if spread is None:
                        return None
                    
                    home_team = row.get('home_team_normalized', row.get('team_home', ''))
                    favorite = str(row.get(favorite_col, ''))
                    
                    if home_team.lower() in str(favorite).lower():
                        return -abs(spread)
                    else:
                        return abs(spread)
                
                df['home_spread'] = df.apply(calculate_home_spread, axis=1)
            else:
                df['home_spread'] = df[spread_col].apply(utils.safe_float)
        else:
            logger.warning("Could not find spread column in data")
            df['home_spread'] = None
    
    # Extract weather data
    # nflfastR has 'temp' and 'wind', Spreadspoke has 'weather_temperature' and 'weather_wind_mph'
    if 'temp' in df.columns:
        df['temperature'] = df['temp'].apply(utils.safe_float)
    elif 'weather_temperature' in df.columns:
        df['temperature'] = df['weather_temperature'].apply(utils.safe_float)
    elif 'temperature' in df.columns:
        df['temperature'] = df['temperature'].apply(utils.safe_float)
    else:
        df['temperature'] = None
    
    if 'wind' in df.columns:
        df['wind_speed'] = df['wind'].apply(utils.safe_float)
    elif 'weather_wind_mph' in df.columns:
        df['wind_speed'] = df['weather_wind_mph'].apply(utils.safe_float)
    else:
        df['wind_speed'] = None
    
    # Weather conditions
    if 'roof' in df.columns:
        # nflfastR has 'roof' field (outdoors, indoors, dome, open, closed)
        df['weather_conditions'] = df['roof']
    elif 'weather_detail' in df.columns:
        df['weather_conditions'] = df['weather_detail']
    elif 'conditions' in df.columns:
        df['weather_conditions'] = df['conditions']
    else:
        df['weather_conditions'] = None
    
    # Extract QB information
    # nflfastR has 'home_qb_id' and 'away_qb_id' - we'll need to map these to names
    # For now, store the IDs and can enrich later
    if 'home_qb_id' in df.columns:
        df['home_qb_id'] = df['home_qb_id']
    else:
        df['home_qb_id'] = None
    
    if 'away_qb_id' in df.columns:
        df['away_qb_id'] = df['away_qb_id']
    else:
        df['away_qb_id'] = None
    
    # QB names (to be filled by fetching player data)
    df['home_qb'] = None
    df['away_qb'] = None
    
    # Coach data (not in nflfastR schedules, need to fetch separately)
    df['home_coach'] = None
    df['away_coach'] = None
    
    # Map scores - nflfastR uses 'home_score' and 'away_score'
    if 'home_score' in df.columns and 'score_home' not in df.columns:
        df['score_home'] = df['home_score']
        df['score_away'] = df['away_score']
    
    logger.info(f"Enriched {len(df)} games with additional data")
    return df


def collect_all_data() -> pd.DataFrame:
    """
    Main function to collect all required data.
    Primary source: nflfastR
    Fallback: Spreadspoke.com
    
    Returns:
        DataFrame with all game data including spreads, weather, etc.
    """
    logger.info("Starting data collection...")
    
    # Primary: Download from nflfastR
    df = download_nflfastr_data()
    
    # If nflfastR fails or is missing data, try Spreadspoke as fallback
    if df.empty or len(df) < 100:  # Arbitrary threshold to check if we got reasonable data
        logger.warning("nflfastR data incomplete or unavailable, trying Spreadspoke as fallback...")
        spreadspoke_df = download_spreadspoke_data()
        
        if not spreadspoke_df.empty:
            if df.empty:
                df = spreadspoke_df
            else:
                # Combine both sources
                logger.info("Combining nflfastR and Spreadspoke data...")
                df = pd.concat([df, spreadspoke_df], ignore_index=True)
                df = df.drop_duplicates(subset=['game_id'] if 'game_id' in df.columns else ['gameday', 'home_team', 'away_team'], keep='first')
    
    if df.empty:
        logger.error("No data collected. Please check data sources.")
        return df
    
    # Filter to relevant seasons
    df = enrich_game_data(df)
    
    # Filter to specified seasons (or use available data if requested range not available)
    if 'season' in df.columns:
        original_count = len(df)
        available_seasons = sorted(df['season'].dropna().unique())
        filtered_df = df[(df['season'] >= config.START_SEASON) & (df['season'] <= config.END_SEASON)]
        
        if len(filtered_df) == 0 and original_count > 0:
            logger.warning(f"No games found in requested range {config.START_SEASON}-{config.END_SEASON}")
            logger.warning(f"Available seasons in data: {available_seasons}")
            logger.warning("NOTE: Spreadspoke.com only provides current season data via direct download.")
            logger.warning("Using available data for analysis (may not match requested date range)...")
            df = df  # Use all available data instead of filtering
            logger.info(f"Using {len(df)} games from available seasons: {available_seasons}")
        else:
            df = filtered_df
            logger.info(f"Filtered to {len(df)} games from {config.START_SEASON}-{config.END_SEASON} (from {original_count} total games)")
    
    # Note: QB and coach data fetching would be done here
    # For now, we'll leave those as None and they can be filled manually or via additional scraping
    
    return df

