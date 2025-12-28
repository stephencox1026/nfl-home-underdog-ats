"""
Configuration file for NFL Home Underdog Divisional ATS Analysis
"""

# Analysis parameters
START_SEASON = 2014
END_SEASON = 2024
SPREAD_THRESHOLD = 3.5  # Home team must be underdog by at least this many points

# Data sources
SPREADSPOKE_DATA_URL = "https://www.spreadspoke.com/data.html"
SPREADSPOKE_CSV_URL = "https://www.spreadspoke.com/nfl.csv"  # Historical NFL data

# NFL divisions (for identifying divisional matchups)
NFL_DIVISIONS = {
    'AFC East': ['Buffalo Bills', 'Miami Dolphins', 'New England Patriots', 'New York Jets'],
    'AFC North': ['Baltimore Ravens', 'Cincinnati Bengals', 'Cleveland Browns', 'Pittsburgh Steelers'],
    'AFC South': ['Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Tennessee Titans'],
    'AFC West': ['Denver Broncos', 'Kansas City Chiefs', 'Las Vegas Raiders', 'Los Angeles Chargers', 'Oakland Raiders', 'San Diego Chargers'],
    'NFC East': ['Dallas Cowboys', 'New York Giants', 'Philadelphia Eagles', 'Washington Commanders', 'Washington Redskins'],
    'NFC North': ['Chicago Bears', 'Detroit Lions', 'Green Bay Packers', 'Minnesota Vikings'],
    'NFC South': ['Atlanta Falcons', 'Carolina Panthers', 'New Orleans Saints', 'Tampa Bay Buccaneers'],
    'NFC West': ['Arizona Cardinals', 'Los Angeles Rams', 'San Francisco 49ers', 'Seattle Seahawks', 'St. Louis Rams']
}

# Team name mappings (handle name changes and variations)
TEAM_NAME_MAPPINGS = {
    'Washington Redskins': 'Washington Commanders',
    'Oakland Raiders': 'Las Vegas Raiders',
    'San Diego Chargers': 'Los Angeles Chargers',
    'St. Louis Rams': 'Los Angeles Rams'
}

# Output directory
OUTPUT_DIR = "outputs"

# Report settings
REPORT_TITLE = "NFL Home Underdog Divisional Game ATS Analysis"
REPORT_SUBTITLE = f"Analysis of games from {START_SEASON}-{END_SEASON} where home team was underdog by {SPREAD_THRESHOLD}+ points"

