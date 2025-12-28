"""
Playoff status calculator - determines if teams were eliminated from playoff contention.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime
import logging
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_team_record_at_date(df: pd.DataFrame, team: str, game_date: datetime) -> Tuple[int, int, int]:
    """
    Calculate a team's win-loss-tie record up to (but not including) a specific date.
    
    Args:
        df: DataFrame with all games
        team: Team name
        game_date: Date to calculate record up to
        
    Returns:
        Tuple of (wins, losses, ties)
    """
    if not game_date:
        return 0, 0, 0
    
    # Get all games for this team before the specified date
    team_games = df[
        (df['game_date'] < game_date) &
        (
            (df['home_team_normalized'] == team) |
            (df['away_team_normalized'] == team)
        )
    ].copy()
    
    wins = 0
    losses = 0
    ties = 0
    
    for _, game in team_games.iterrows():
        home_team = game.get('home_team_normalized', '')
        away_team = game.get('away_team_normalized', '')
        home_score = utils.safe_float(game.get('score_home', game.get('score_1', None)))
        away_score = utils.safe_float(game.get('score_away', game.get('score_2', None)))
        
        if home_score is None or away_score is None:
            continue
        
        if home_team == team:
            if home_score > away_score:
                wins += 1
            elif home_score < away_score:
                losses += 1
            else:
                ties += 1
        elif away_team == team:
            if away_score > home_score:
                wins += 1
            elif away_score < home_score:
                losses += 1
            else:
                ties += 1
    
    return wins, losses, ties


def calculate_games_remaining(season: int, week: int) -> int:
    """
    Calculate number of games remaining in the season.
    
    Args:
        season: Season year
        week: Current week number
        
    Returns:
        Number of games remaining
    """
    # NFL regular season is 17 games per team (since 2021, was 16 before)
    if season >= 2021:
        total_games = 17
    else:
        total_games = 16
    
    # Approximate: assume 1 game per week
    games_played = week
    remaining = max(0, total_games - games_played)
    
    return remaining


def is_eliminated_from_playoffs(
    wins: int, 
    losses: int, 
    ties: int, 
    games_remaining: int,
    division: Optional[str] = None
) -> bool:
    """
    Determine if a team is mathematically eliminated from playoff contention.
    This is a simplified version - full calculation would require division/conference standings.
    
    Args:
        wins: Current wins
        losses: Current losses
        ties: Current ties
        games_remaining: Games remaining in season
        division: Division name (optional, for more accurate calculation)
        
    Returns:
        True if eliminated, False if still in contention
    """
    if games_remaining == 0:
        # Season is over - check if they made playoffs
        # This is simplified - would need actual playoff data
        return False  # Can't determine without playoff data
    
    # Maximum possible wins
    max_wins = wins + games_remaining
    
    # Simplified elimination: if max wins is less than typical wild card threshold, likely eliminated
    # In reality, need to check against all other teams' possible records
    # For now, use a heuristic: if max wins < 9, likely eliminated (9-8 or better usually needed)
    
    # More conservative: if they can't reach 9 wins and it's late in season, likely eliminated
    if max_wins < 9 and games_remaining <= 3:
        return True
    
    # Very early in season - can't be eliminated yet
    if games_remaining >= 10:
        return False
    
    # This is a simplified check - full implementation would need:
    # 1. Current division standings
    # 2. Current conference standings
    # 3. Remaining schedule for all teams
    # 4. Mathematical elimination calculations
    
    return False  # Default to not eliminated (conservative)


def add_playoff_status_to_games(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add playoff elimination status for both teams in each game.
    
    Args:
        df: DataFrame with game data
        
    Returns:
        DataFrame with playoff status columns added
    """
    logger.info("Calculating playoff elimination status...")
    
    df['home_eliminated'] = False
    df['away_eliminated'] = False
    
    # Sort by date to process chronologically
    df_sorted = df.sort_values('game_date').copy()
    
    # For each game, calculate records up to that point
    for idx, game in df_sorted.iterrows():
        game_date = game.get('game_date')
        season = game.get('season')
        week = game.get('week')
        
        if not game_date or not season:
            continue
        
        home_team = game.get('home_team_normalized', '')
        away_team = game.get('away_team_normalized', '')
        
        if not home_team or not away_team:
            continue
        
        # Calculate records
        home_wins, home_losses, home_ties = calculate_team_record_at_date(
            df_sorted, home_team, game_date
        )
        away_wins, away_losses, away_ties = calculate_team_record_at_date(
            df_sorted, away_team, game_date
        )
        
        # Calculate games remaining
        games_remaining = calculate_games_remaining(season, week)
        
        # Get divisions
        home_division = utils.get_division(home_team)
        away_division = utils.get_division(away_team)
        
        # Check elimination status
        home_eliminated = is_eliminated_from_playoffs(
            home_wins, home_losses, home_ties, games_remaining, home_division
        )
        away_eliminated = is_eliminated_from_playoffs(
            away_wins, away_losses, away_ties, games_remaining, away_division
        )
        
        # Update DataFrame
        df.loc[idx, 'home_eliminated'] = home_eliminated
        df.loc[idx, 'away_eliminated'] = away_eliminated
        df.loc[idx, 'home_wins'] = home_wins
        df.loc[idx, 'home_losses'] = home_losses
        df.loc[idx, 'away_wins'] = away_wins
        df.loc[idx, 'away_losses'] = away_losses
    
    logger.info("Playoff status calculation complete")
    return df

