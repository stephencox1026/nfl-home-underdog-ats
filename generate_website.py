"""
Generate mobile-friendly HTML website for NFL analysis.
"""

import pandas as pd
from pathlib import Path
import config

def generate_mobile_website():
    """Generate a mobile-friendly HTML website from the games data."""
    
    # Load the games data
    games_file = Path(config.OUTPUT_DIR) / "games_list.csv"
    if not games_file.exists():
        print(f"Error: {games_file} not found. Please run main.py first to generate data.")
        return
    
    df = pd.read_csv(games_file)
    
    # Convert date column
    if 'game_date' in df.columns:
        df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
    
    # Group by season
    seasons = sorted(df['season'].dropna().unique().astype(int), reverse=True)
    
    # Generate HTML
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFL Home Underdog Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #1E3A5F;
            color: #000000;
            padding: 20px 10px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
        }
        
        .header h1 {
            color: #FFFFFF;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .header p {
            color: #CCCCCC;
            font-size: 14px;
        }
        
        .ad-box {
            background-color: #B0B0B0;
            border: 1px solid #000000;
            border-radius: 4px;
            padding: 20px;
            margin: 20px 0;
            margin-bottom: 30px;
        }
        
        .ad-title {
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .ad-body {
            font-size: 16px;
            color: #000000;
            line-height: 1.6;
        }
        
        .season-section {
            background-color: #B0B0B0;
            border: 1px solid #000000;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .season-header {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #000000;
            border-bottom: 2px solid #000000;
            padding-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            text-align: center;
            padding: 12px;
            background-color: #FFFFFF;
            border-radius: 4px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 11px;
            color: #666666;
            text-transform: uppercase;
        }
        
        .win-rate {
            color: #1B5E20;
        }
        
        .win-rate.low {
            color: #B71C1C;
        }
        
        .status {
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status.profitable {
            color: #1B5E20;
        }
        
        .status.not-profitable {
            color: #B71C1C;
        }
        
        .games-toggle {
            background-color: #000000;
            color: #FFFFFF;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            margin-top: 15px;
            width: 100%;
        }
        
        .games-toggle:hover {
            background-color: #333333;
        }
        
        .games-table {
            display: none;
            margin-top: 20px;
            overflow-x: auto;
        }
        
        .games-table.show {
            display: block;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #FFFFFF;
            font-size: 14px;
        }
        
        thead {
            background-color: #B0B0B0;
        }
        
        th {
            padding: 12px 8px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #000000;
        }
        
        td {
            padding: 10px 8px;
            border-bottom: 1px solid #E0E0E0;
        }
        
        tbody tr:nth-child(even) {
            background-color: #F8F8F8;
        }
        
        tbody tr:nth-child(odd) {
            background-color: #FFFFFF;
        }
        
        .cover {
            color: #1B5E20;
            font-weight: bold;
        }
        
        .loss {
            color: #B71C1C;
            font-weight: bold;
        }
        
        .push {
            color: #9E9E9E;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 24px;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .ad-title {
                font-size: 18px;
            }
            
            .ad-body {
                font-size: 14px;
            }
            
            table {
                font-size: 12px;
            }
            
            th, td {
                padding: 8px 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NFL Home Underdog Analysis</h1>
            <p>Divisional Games • Home Underdogs 3.5+ Points</p>
        </div>
"""
    
    # Add seasons
    for season in seasons:
        season_data = df[df['season'] == season].copy()
        
        if len(season_data) == 0:
            continue
        
        # Calculate stats
        total_games = len(season_data)
        covers = season_data['home_covered'].sum() if 'home_covered' in season_data.columns else 0
        losses = (~season_data['home_covered']).sum() if 'home_covered' in season_data.columns else 0
        games_with_result = covers + losses
        win_rate = (covers / games_with_result * 100) if games_with_result > 0 else 0
        is_profitable = win_rate > 52.4
        
        # Add ad box for 2024
        if season == 2024:
            html += """
        <div class="ad-box">
            <div class="ad-title">🎬 Coming 2026: The Richard Sondgroth Story 🎬</div>
            <div class="ad-body">
                A good-hearted Texan who's got two passions: the perfect pair of kicks and the best BBQ in the Lone Star State. 
                When he's not hunting down rare sneakers or perfecting his brisket, he's just being an all-around great guy. 
                But behind the scenes, there's a complicated love story unfolding with a man who keeps him on his toes - 
                a relationship full of passion, late-night conversations, and the kind of drama that makes life interesting. 
                This one's for you, Richard! 🤠👟🍖💕
            </div>
        </div>
"""
        
        html += f"""
        <div class="season-section">
            <div class="season-header">Season {int(season)}</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{total_games}</div>
                    <div class="stat-label">Total Games</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{covers}</div>
                    <div class="stat-label">Covers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{losses}</div>
                    <div class="stat-label">Losses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value {'win-rate' if win_rate > 50 else 'win-rate low'}">{win_rate:.1f}%</div>
                    <div class="stat-label">Win Rate</div>
                </div>
            </div>
            <div class="status {'profitable' if is_profitable else 'not-profitable'}">
                {'✓ Profitable' if is_profitable else '✗ Not Profitable'}
            </div>
            <button class="games-toggle" onclick="toggleGames('season-{int(season)}')">View Games ▼</button>
            <div class="games-table" id="season-{int(season)}">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Visiting</th>
                            <th>Home</th>
                            <th>Spread</th>
                            <th>Score</th>
                            <th>Result</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Sort by date
        season_data = season_data.sort_values('game_date')
        
        for idx, row in season_data.iterrows():
            visiting = str(row.get('away_team_normalized', ''))
            home = str(row.get('home_team_normalized', ''))
            
            spread_val = row.get('home_spread', None)
            if pd.notna(spread_val):
                spread = f"+{spread_val:.1f}" if spread_val > 0 else f"{spread_val:.1f}"
            else:
                spread = "N/A"
            
            home_score = row.get('home_score', row.get('score_home', None))
            away_score = row.get('away_score', row.get('score_away', None))
            if pd.notna(home_score) and pd.notna(away_score):
                score = f"{int(home_score)} - {int(away_score)}"
            else:
                score = "N/A"
            
            home_covered = bool(row.get('home_covered', False)) if pd.notna(row.get('home_covered', False)) else False
            ats_result = str(row.get('ats_result', ''))
            
            if home_covered:
                result_class = "cover"
                result_text = "Cover"
            elif ats_result == 'Push':
                result_class = "push"
                result_text = "Push"
            else:
                result_class = "loss"
                result_text = "Loss"
            
            game_date = row.get('game_date', '')
            if pd.notna(game_date):
                try:
                    date_str = pd.to_datetime(game_date).strftime('%m/%d/%Y')
                except:
                    date_str = str(game_date)[:10] if len(str(game_date)) > 10 else str(game_date)
            else:
                date_str = "N/A"
            
            html += f"""
                        <tr>
                            <td>{date_str}</td>
                            <td>{visiting}</td>
                            <td>{home}</td>
                            <td>{spread}</td>
                            <td>{score}</td>
                            <td class="{result_class}">{result_text}</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
"""
    
    html += """
    </div>
    
    <script>
        function toggleGames(seasonId) {
            const table = document.getElementById(seasonId);
            const button = table.previousElementSibling;
            
            if (table.classList.contains('show')) {
                table.classList.remove('show');
                button.textContent = 'View Games ▼';
            } else {
                table.classList.add('show');
                button.textContent = 'Hide Games ▲';
            }
        }
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_file = Path(config.OUTPUT_DIR) / "mobile_website.html"
    output_file.write_text(html, encoding='utf-8')
    print(f"Mobile website generated: {output_file}")
    print(f"\nTo view locally, run: python serve_website.py")
    print(f"Then open: http://localhost:8000/mobile_website.html")
    print(f"\nTo share with friends:")
    print(f"1. Use a service like ngrok: ngrok http 8000")
    print(f"2. Or upload to a free hosting service like Netlify, Vercel, or GitHub Pages")

if __name__ == "__main__":
    generate_mobile_website()

