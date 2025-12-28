"""
Enrichment module for QB and Coach data.
This module adds QB and coach information to existing game data without modifying other fields.
"""

import pandas as pd
import logging
from typing import Dict, Optional
from datetime import datetime

try:
    import nfl_data_py as nfl
    HAS_NFL_DATA = True
except ImportError:
    HAS_NFL_DATA = False
    logging.warning("nfl-data-py not installed. Install with: pip install nfl-data-py")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for player and coach data to avoid repeated API calls
_player_cache: Dict[str, str] = {}
_coach_cache: Dict[tuple, str] = {}  # Key: (season, team)


def get_qb_name_from_id(qb_id: Optional[str], season: int) -> Optional[str]:
    """
    Get quarterback name from QB ID using nfl-data-py.
    
    Args:
        qb_id: Quarterback ID from nflfastR
        season: Season year
        
    Returns:
        Quarterback name or None
    """
    if not HAS_NFL_DATA or pd.isna(qb_id) or qb_id is None:
        return None
    
    qb_id_str = str(qb_id)
    
    # Check cache first
    cache_key = f"{season}_{qb_id_str}"
    if cache_key in _player_cache:
        return _player_cache[cache_key]
    
    try:
        # Import roster data for the season
        rosters = nfl.import_rosters([season])
        
        if rosters.empty or 'player_name' not in rosters.columns:
            return None
        
        # Find player by ID
        player = rosters[rosters.get('player_id', pd.Series()) == qb_id_str]
        if not player.empty and 'player_name' in player.columns:
            qb_name = player.iloc[0]['player_name']
            _player_cache[cache_key] = qb_name
            return qb_name
        
        # Try with gsis_id or other ID fields
        for id_col in ['gsis_id', 'espn_id', 'sportradar_id']:
            if id_col in rosters.columns:
                player = rosters[rosters[id_col] == qb_id_str]
                if not player.empty and 'player_name' in player.columns:
                    qb_name = player.iloc[0]['player_name']
                    _player_cache[cache_key] = qb_name
                    return qb_name
        
    except Exception as e:
        logger.warning(f"Error fetching QB name for ID {qb_id_str} in season {season}: {e}")
    
    return None


def get_coach_by_season_team(season: int, team: str) -> Optional[str]:
    """
    Get head coach for a team in a specific season.
    Uses nfl-data-py coaching data if available, otherwise uses a static mapping.
    
    Args:
        season: Season year
        team: Team name (normalized)
        
    Returns:
        Head coach name or None
    """
    if not HAS_NFL_DATA:
        return None
    
    # Check cache
    cache_key = (season, team)
    if cache_key in _coach_cache:
        return _coach_cache[cache_key]
    
    try:
        # Try to get coaching data from nfl-data-py
        # Note: nfl-data-py may not have direct coach data in all versions
        coaches_df = None
        try:
            # Try importing coaches data (if available in this version)
            if hasattr(nfl, 'import_coaches'):
                coaches_df = nfl.import_coaches([season])
        except (AttributeError, Exception) as e:
            logger.debug(f"Coach import not available: {e}")
        
        if coaches_df is not None and not coaches_df.empty:
            # Try to match team - would need team name normalization
            # For now, skip this as it requires additional mapping
            pass
        
    except Exception as e:
        logger.debug(f"Error fetching coach for {team} in season {season}: {e}")
    
    # Fallback: Use a basic mapping (this is a simplified approach)
    # For a complete solution, you'd want to scrape Pro-Football-Reference
    # or use a more comprehensive data source
    coach_name = _get_coach_from_static_mapping(season, team)
    if coach_name:
        _coach_cache[cache_key] = coach_name
        return coach_name
    
    # Return None to indicate data is not available
    # This preserves existing data and only fills in where we have information
    return None


def _get_coach_from_static_mapping(season: int, team: str) -> Optional[str]:
    """
    Basic static mapping of coaches by season and team.
    This is a fallback - for complete data, you'd want to scrape or use an API.
    
    Args:
        season: Season year
        team: Team name
        
    Returns:
        Coach name or None
    """
    # This is a placeholder - you could expand this with actual coach data
    # For now, return None to indicate data is not available
    # A full implementation would scrape Pro-Football-Reference or use an API
    return None


def enrich_qb_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich DataFrame with quarterback names from QB IDs.
    Only updates rows where home_qb or away_qb is None/empty.
    Does not modify any other existing data.
    
    Args:
        df: DataFrame with game data including home_qb_id and away_qb_id
        
    Returns:
        DataFrame with enriched QB names
    """
    if df.empty:
        return df
    
    logger.info("Enriching QB data...")
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Get unique seasons for batch processing
    seasons = df['season'].dropna().unique().astype(int) if 'season' in df.columns else []
    
    enriched_count = 0
    
    # Enrich home QB names
    if 'home_qb_id' in df.columns and 'home_qb' in df.columns:
        mask = (df['home_qb'].isna() | (df['home_qb'] == '')) & df['home_qb_id'].notna()
        for idx in df[mask].index:
            qb_id = df.loc[idx, 'home_qb_id']
            season = int(df.loc[idx, 'season']) if pd.notna(df.loc[idx, 'season']) else None
            if season:
                qb_name = get_qb_name_from_id(qb_id, season)
                if qb_name:
                    df.loc[idx, 'home_qb'] = qb_name
                    enriched_count += 1
    
    # Enrich away QB names
    if 'away_qb_id' in df.columns and 'away_qb' in df.columns:
        mask = (df['away_qb'].isna() | (df['away_qb'] == '')) & df['away_qb_id'].notna()
        for idx in df[mask].index:
            qb_id = df.loc[idx, 'away_qb_id']
            season = int(df.loc[idx, 'season']) if pd.notna(df.loc[idx, 'season']) else None
            if season:
                qb_name = get_qb_name_from_id(qb_id, season)
                if qb_name:
                    df.loc[idx, 'away_qb'] = qb_name
                    enriched_count += 1
    
    logger.info(f"Enriched {enriched_count} QB names")
    return df


def enrich_coach_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich DataFrame with head coach names.
    Only updates rows where home_coach or away_coach is None/empty.
    Does not modify any other existing data.
    
    Args:
        df: DataFrame with game data
        
    Returns:
        DataFrame with enriched coach names
    """
    if df.empty:
        return df
    
    logger.info("Enriching coach data...")
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    enriched_count = 0
    
    # Enrich home coach names
    if 'home_coach' in df.columns and 'home_team_normalized' in df.columns:
        mask = (df['home_coach'].isna() | (df['home_coach'] == '')) & df['season'].notna()
        for idx in df[mask].index:
            team = df.loc[idx, 'home_team_normalized']
            season = int(df.loc[idx, 'season']) if pd.notna(df.loc[idx, 'season']) else None
            if season and team:
                coach_name = get_coach_by_season_team(season, team)
                if coach_name:
                    df.loc[idx, 'home_coach'] = coach_name
                    enriched_count += 1
    
    # Enrich away coach names
    if 'away_coach' in df.columns and 'away_team_normalized' in df.columns:
        mask = (df['away_coach'].isna() | (df['away_coach'] == '')) & df['season'].notna()
        for idx in df[mask].index:
            team = df.loc[idx, 'away_team_normalized']
            season = int(df.loc[idx, 'season']) if pd.notna(df.loc[idx, 'season']) else None
            if season and team:
                coach_name = get_coach_by_season_team(season, team)
                if coach_name:
                    df.loc[idx, 'away_coach'] = coach_name
                    enriched_count += 1
    
    logger.info(f"Enriched {enriched_count} coach names")
    return df


def enrich_all_additional_data(df: pd.DataFrame, preserve_existing: bool = True) -> pd.DataFrame:
    """
    Enrich DataFrame with QB and coach data.
    This function only adds missing QB/coach data and does not modify existing data.
    
    Args:
        df: DataFrame with game data
        preserve_existing: If True, only fills in None/empty values, never overwrites existing data
        
    Returns:
        Enriched DataFrame
    """
    if df.empty:
        return df
    
    logger.info("Starting QB and coach enrichment (preserving existing data)...")
    
    # Make a copy to ensure we don't modify the original
    df = df.copy()
    
    # Enrich QB data (only fills missing values)
    df = enrich_qb_data(df)
    
    # Enrich coach data (only fills missing values)
    df = enrich_coach_data(df)
    
    logger.info("QB and coach enrichment complete")
    return df

