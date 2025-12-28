"""
Game filter and ATS analyzer for NFL home underdog divisional games.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging
import config
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def filter_qualifying_games(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter games where home team is underdog by 3.5+ points in divisional matchups.
    
    Args:
        df: DataFrame with all game data
        
    Returns:
        Filtered DataFrame with qualifying games
    """
    logger.info("Filtering qualifying games...")
    
    # Start with all games
    filtered = df.copy()
    
    # Filter: Home team is underdog by threshold or more
    # Home spread > 0 means home is underdog (positive spread = home gets points)
    filtered = filtered[
        (filtered['home_spread'].notna()) &
        (filtered['home_spread'] >= config.SPREAD_THRESHOLD)
    ]
    
    logger.info(f"After spread filter: {len(filtered)} games")
    
    # Filter: Divisional matchups
    filtered = filtered[filtered['is_divisional'] == True]
    
    logger.info(f"After divisional filter: {len(filtered)} games")
    
    # Filter: Must have scores to calculate ATS
    score_cols = ['score_home', 'score_away', 'score_1', 'score_2']
    has_scores = False
    for col in score_cols:
        if col in filtered.columns:
            filtered = filtered[
                filtered[col].notna()
            ]
            has_scores = True
            break
    
    if not has_scores:
        logger.warning("Could not find score columns - ATS calculation may fail")
    
    logger.info(f"Final qualifying games: {len(filtered)}")
    
    return filtered


def calculate_ats_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ATS results for home teams.
    
    Args:
        df: DataFrame with qualifying games
        
    Returns:
        DataFrame with ATS results added
    """
    logger.info("Calculating ATS results...")
    
    df = df.copy()
    
    # Get scores
    home_score_col = None
    away_score_col = None
    
    for col in ['score_home', 'score_1']:
        if col in df.columns:
            home_score_col = col
            break
    
    for col in ['score_away', 'score_2']:
        if col in df.columns:
            away_score_col = col
            break
    
    if not home_score_col or not away_score_col:
        logger.error("Could not find score columns")
        df['ats_result'] = None
        return df
    
    # Calculate ATS result
    df['home_score'] = df[home_score_col].apply(utils.safe_float)
    df['away_score'] = df[away_score_col].apply(utils.safe_float)
    
    df['ats_result'] = df.apply(
        lambda row: utils.calculate_ats_result(
            row['home_score'],
            row['away_score'],
            row['home_spread']
        ),
        axis=1
    )
    
    # Calculate if home team covered
    df['home_covered'] = df['ats_result'] == 'Cover'
    df['home_pushed'] = df['ats_result'] == 'Push'
    df['home_lost_ats'] = df['ats_result'] == 'Loss'
    
    logger.info(f"ATS results calculated for {len(df)} games")
    
    return df


def generate_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for the analysis.
    
    Args:
        df: DataFrame with qualifying games and ATS results
        
    Returns:
        Dictionary with summary statistics
    """
    logger.info("Generating summary statistics...")
    
    total_games = len(df)
    
    if total_games == 0:
        return {
            'total_games': 0,
            'home_ats_wins': 0,
            'home_ats_losses': 0,
            'home_ats_pushes': 0,
            'home_ats_win_rate': 0.0
        }
    
    # ATS results
    covers = df['home_covered'].sum()
    losses = df['home_lost_ats'].sum()
    pushes = df['home_pushed'].sum()
    
    # Calculate win rate (excluding pushes)
    games_with_result = covers + losses
    win_rate = (covers / games_with_result * 100) if games_with_result > 0 else 0.0
    
    # By month
    monthly_stats = {}
    if 'month' in df.columns:
        for month in sorted(df['month'].dropna().unique()):
            month_df = df[df['month'] == month]
            month_covers = month_df['home_covered'].sum()
            month_losses = month_df['home_lost_ats'].sum()
            month_total = month_covers + month_losses
            monthly_stats[month] = {
                'total': len(month_df),
                'covers': month_covers,
                'losses': month_losses,
                'win_rate': (month_covers / month_total * 100) if month_total > 0 else 0.0
            }
    
    # By week
    weekly_stats = {}
    if 'week' in df.columns:
        for week in sorted(df['week'].dropna().unique()):
            week_df = df[df['week'] == week]
            week_covers = week_df['home_covered'].sum()
            week_losses = week_df['home_lost_ats'].sum()
            week_total = week_covers + week_losses
            weekly_stats[week] = {
                'total': len(week_df),
                'covers': week_covers,
                'losses': week_losses,
                'win_rate': (week_covers / week_total * 100) if week_total > 0 else 0.0
            }
    
    # By playoff status
    playoff_stats = {}
    if 'home_eliminated' in df.columns and 'away_eliminated' in df.columns:
        # Both teams still in contention
        both_in = df[(df['home_eliminated'] == False) & (df['away_eliminated'] == False)]
        both_covers = both_in['home_covered'].sum()
        both_losses = both_in['home_lost_ats'].sum()
        both_total = both_covers + both_losses
        playoff_stats['both_in_contention'] = {
            'total': len(both_in),
            'covers': both_covers,
            'losses': both_losses,
            'win_rate': (both_covers / both_total * 100) if both_total > 0 else 0.0
        }
        
        # Home eliminated, away in contention
        home_out = df[(df['home_eliminated'] == True) & (df['away_eliminated'] == False)]
        home_out_covers = home_out['home_covered'].sum()
        home_out_losses = home_out['home_lost_ats'].sum()
        home_out_total = home_out_covers + home_out_losses
        playoff_stats['home_eliminated'] = {
            'total': len(home_out),
            'covers': home_out_covers,
            'losses': home_out_losses,
            'win_rate': (home_out_covers / home_out_total * 100) if home_out_total > 0 else 0.0
        }
        
        # Away eliminated, home in contention
        away_out = df[(df['home_eliminated'] == False) & (df['away_eliminated'] == True)]
        away_out_covers = away_out['home_covered'].sum()
        away_out_losses = away_out['home_lost_ats'].sum()
        away_out_total = away_out_covers + away_out_losses
        playoff_stats['away_eliminated'] = {
            'total': len(away_out),
            'covers': away_out_covers,
            'losses': away_out_losses,
            'win_rate': (away_out_covers / away_out_total * 100) if away_out_total > 0 else 0.0
        }
        
        # Both eliminated
        both_out = df[(df['home_eliminated'] == True) & (df['away_eliminated'] == True)]
        both_out_covers = both_out['home_covered'].sum()
        both_out_losses = both_out['home_lost_ats'].sum()
        both_out_total = both_out_covers + both_out_losses
        playoff_stats['both_eliminated'] = {
            'total': len(both_out),
            'covers': both_out_covers,
            'losses': both_out_losses,
            'win_rate': (both_out_covers / both_out_total * 100) if both_out_total > 0 else 0.0
        }
    
    stats = {
        'total_games': total_games,
        'home_ats_wins': int(covers),
        'home_ats_losses': int(losses),
        'home_ats_pushes': int(pushes),
        'home_ats_win_rate': round(win_rate, 2),
        'monthly_breakdown': monthly_stats,
        'weekly_breakdown': weekly_stats,
        'playoff_status_breakdown': playoff_stats
    }
    
    logger.info(f"Summary stats generated: {covers} covers, {losses} losses, {win_rate:.2f}% win rate")
    
    return stats


def analyze_games(df: pd.DataFrame) -> tuple:
    """
    Main analysis function - filters games and calculates ATS results.
    
    Args:
        df: DataFrame with all game data
        
    Returns:
        Tuple of (filtered_games_df, summary_stats_dict)
    """
    logger.info("Starting game analysis...")
    
    # Filter qualifying games
    filtered = filter_qualifying_games(df)
    
    if len(filtered) == 0:
        logger.warning("No qualifying games found")
        return filtered, {}
    
    # Calculate ATS results
    filtered = calculate_ats_results(filtered)
    
    # Generate summary statistics
    stats = generate_summary_stats(filtered)
    
    return filtered, stats

