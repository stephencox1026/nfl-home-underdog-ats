"""
Utility functions for NFL analysis
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Tuple
import config


def normalize_team_name(team_name: str) -> str:
    """
    Normalize team names to handle variations and name changes.
    
    Args:
        team_name: Raw team name from data source
        
    Returns:
        Normalized team name
    """
    if not team_name:
        return team_name
    
    # Apply team name mappings
    for old_name, new_name in config.TEAM_NAME_MAPPINGS.items():
        if old_name.lower() in team_name.lower():
            return new_name
    
    return team_name.strip()


def get_division(team_name: str) -> Optional[str]:
    """
    Get the division for a given team.
    
    Args:
        team_name: Team name
        
    Returns:
        Division name or None if not found
    """
    normalized_name = normalize_team_name(team_name)
    
    for division, teams in config.NFL_DIVISIONS.items():
        for team in teams:
            if normalized_name.lower() == team.lower():
                return division
    
    return None


def are_same_division(team1: str, team2: str) -> bool:
    """
    Check if two teams are in the same division.
    
    Args:
        team1: First team name
        team2: Second team name
        
    Returns:
        True if teams are in same division, False otherwise
    """
    div1 = get_division(team1)
    div2 = get_division(team2)
    
    return div1 is not None and div2 is not None and div1 == div2


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime object.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime object or None if parsing fails
    """
    if pd.isna(date_str) or not date_str:
        return None
    
    # Try common date formats (M/D/YYYY is common in Spreadspoke)
    date_formats = [
        '%m/%d/%Y',  # Most common in Spreadspoke
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%m-%d-%Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except (ValueError, AttributeError):
            continue
    
    return None


def get_season_week(date: datetime) -> Tuple[int, int]:
    """
    Get season year and week number from date.
    NFL season typically starts in September.
    
    Args:
        date: Game date
        
    Returns:
        Tuple of (season_year, week_number)
    """
    if not date:
        return None, None
    
    # NFL season year is the year in which the season ends (Super Bowl is in February)
    # Regular season typically runs from September to January
    if date.month >= 9:  # September onwards
        season_year = date.year + 1
    else:  # January - August (playoffs/offseason)
        season_year = date.year
    
    # Week calculation is approximate - actual week depends on NFL schedule
    # This is a simplified version
    if date.month >= 9:
        # September onwards - calculate weeks from September 1
        season_start = datetime(date.year, 9, 1)
        week = ((date - season_start).days // 7) + 1
    else:
        # January - part of previous season
        season_start = datetime(date.year - 1, 9, 1)
        week = ((date - season_start).days // 7) + 1
    
    return season_year, min(max(week, 1), 18)  # Clamp to 1-18 weeks


def calculate_ats_result(home_score: float, away_score: float, spread: float) -> str:
    """
    Calculate ATS result for home team.
    
    Args:
        home_score: Home team score
        away_score: Away team score
        spread: Point spread (from home team perspective, negative means home is underdog)
        
    Returns:
        'Cover', 'Push', or 'Loss'
    """
    if pd.isna(home_score) or pd.isna(away_score) or pd.isna(spread):
        return None
    
    # Spread from home perspective: negative means home is underdog
    # If spread is -3.5, home team needs to lose by 3 or less (or win) to cover
    home_margin = home_score - away_score
    
    if home_margin + spread > 0:
        return 'Cover'
    elif home_margin + spread == 0:
        return 'Push'
    else:
        return 'Loss'


def safe_float(value) -> Optional[float]:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        
    Returns:
        float or None if conversion fails
    """
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

