"""
Team abbreviation to full name mappings for NFL teams.
"""

import pandas as pd

# Team abbreviation to full name mapping
TEAM_ABBREV_TO_NAME = {
    'ARI': 'Arizona Cardinals',
    'ATL': 'Atlanta Falcons',
    'BAL': 'Baltimore Ravens',
    'BUF': 'Buffalo Bills',
    'CAR': 'Carolina Panthers',
    'CHI': 'Chicago Bears',
    'CIN': 'Cincinnati Bengals',
    'CLE': 'Cleveland Browns',
    'DAL': 'Dallas Cowboys',
    'DEN': 'Denver Broncos',
    'DET': 'Detroit Lions',
    'GB': 'Green Bay Packers',
    'HOU': 'Houston Texans',
    'IND': 'Indianapolis Colts',
    'JAX': 'Jacksonville Jaguars',
    'JAC': 'Jacksonville Jaguars',
    'KC': 'Kansas City Chiefs',
    'LV': 'Las Vegas Raiders',
    'OAK': 'Oakland Raiders',  # Historical
    'LAC': 'Los Angeles Chargers',
    'SD': 'San Diego Chargers',  # Historical
    'LAR': 'Los Angeles Rams',
    'LA': 'Los Angeles Rams',  # Alternative abbreviation
    'STL': 'St. Louis Rams',  # Historical
    'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings',
    'NE': 'New England Patriots',
    'NO': 'New Orleans Saints',
    'NYG': 'New York Giants',
    'NYJ': 'New York Jets',
    'PHI': 'Philadelphia Eagles',
    'PIT': 'Pittsburgh Steelers',
    'SF': 'San Francisco 49ers',
    'SEA': 'Seattle Seahawks',
    'TB': 'Tampa Bay Buccaneers',
    'TEN': 'Tennessee Titans',
    'WAS': 'Washington Commanders',
    'WSH': 'Washington Commanders',
}

def get_team_name_from_abbrev(abbrev: str) -> str:
    """
    Convert team abbreviation to full name.
    
    Args:
        abbrev: Team abbreviation (e.g., 'KC', 'BUF')
        
    Returns:
        Full team name or original abbrev if not found
    """
    if not abbrev or pd.isna(abbrev):
        return abbrev
    
    abbrev = str(abbrev).upper().strip()
    return TEAM_ABBREV_TO_NAME.get(abbrev, abbrev)

