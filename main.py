"""
Main script for NFL Home Underdog Divisional Game ATS Analysis
"""

import logging
import sys
from datetime import datetime

import data_collector
import playoff_calculator
import analyzer
import report_generator
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main execution function.
    """
    logger.info("=" * 60)
    logger.info("NFL Home Underdog Divisional Game ATS Analysis")
    logger.info(f"Analyzing seasons {config.START_SEASON}-{config.END_SEASON}")
    logger.info(f"Spread threshold: {config.SPREAD_THRESHOLD}+ points")
    logger.info("=" * 60)
    
    try:
        # Step 1: Collect data
        logger.info("\n[Step 1/4] Collecting data...")
        df = data_collector.collect_all_data()
        
        if df.empty:
            logger.error("No data collected. Please check data sources.")
            logger.error("You may need to manually download data from https://www.spreadspoke.com/data.html")
            logger.error("See DATA_SOURCES.md for alternative data source options.")
            return 1
        
        if len(df) == 0:
            logger.warning("No games in the specified date range. Check available data above.")
            return 1
        
        logger.info(f"Collected {len(df)} total games")
        
        # Step 2: Calculate playoff status
        logger.info("\n[Step 2/4] Calculating playoff elimination status...")
        df = playoff_calculator.add_playoff_status_to_games(df)
        
        # Step 3: Analyze games
        logger.info("\n[Step 3/4] Analyzing qualifying games...")
        filtered_df, stats = analyzer.analyze_games(df)
        
        if len(filtered_df) == 0:
            logger.warning("No qualifying games found matching criteria.")
            logger.warning("Criteria: Home team underdog by 3.5+ points in divisional games")
            return 1
        
        logger.info(f"Found {len(filtered_df)} qualifying games")
        logger.info(f"Home team ATS record: {stats.get('home_ats_wins', 0)}-{stats.get('home_ats_losses', 0)}-{stats.get('home_ats_pushes', 0)}")
        logger.info(f"Home team ATS win rate: {stats.get('home_ats_win_rate', 0.0):.2f}%")
        
        # Step 4: Generate reports
        logger.info("\n[Step 4/4] Generating reports...")
        report_generator.generate_all_reports(filtered_df, stats)
        
        logger.info("\n" + "=" * 60)
        logger.info("Analysis complete!")
        logger.info(f"Reports saved to: {config.OUTPUT_DIR}/")
        logger.info("=" * 60)
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total Qualifying Games: {stats.get('total_games', 0)}")
        print(f"Home ATS Wins: {stats.get('home_ats_wins', 0)}")
        print(f"Home ATS Losses: {stats.get('home_ats_losses', 0)}")
        print(f"Home ATS Pushes: {stats.get('home_ats_pushes', 0)}")
        print(f"ATS Win Rate: {stats.get('home_ats_win_rate', 0.0):.2f}%")
        
        if stats.get('home_ats_win_rate', 0) > 52.4:
            print("\n✓ There appears to be VALUE in this betting strategy")
            print("  (Win rate exceeds break-even point of 52.4% at -110 odds)")
        elif stats.get('home_ats_win_rate', 0) > 50:
            print("\n~ Win rate is slightly above break-even")
            print("  (May not provide significant value after accounting for variance)")
        else:
            print("\n✗ There does NOT appear to be value in this betting strategy")
            print("  (Win rate is below break-even point)")
        
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

