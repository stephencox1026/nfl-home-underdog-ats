"""
Report generator for CSV and HTML reports.
"""

import pandas as pd
import os
from typing import Dict
import logging
import config
from jinja2 import Template
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    sns.set_style("whitegrid")
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style for plots
plt.rcParams['figure.figsize'] = (12, 6)


def generate_csv_reports(df: pd.DataFrame, stats: Dict) -> None:
    """
    Generate CSV files with game data and summary statistics.
    
    Args:
        df: DataFrame with qualifying games
        stats: Summary statistics dictionary
    """
    logger.info("Generating CSV reports...")
    
    # Ensure output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Full games list
    games_file = os.path.join(config.OUTPUT_DIR, "games_list.csv")
    
    # Select columns for export
    export_cols = [
        'game_date', 'season', 'week', 'month',
        'home_team_normalized', 'away_team_normalized',
        'home_score', 'away_score', 'home_spread',
        'ats_result', 'home_covered',
        'temperature', 'wind_speed', 'weather_conditions',
        'home_qb', 'away_qb', 'home_coach', 'away_coach',
        'home_eliminated', 'away_eliminated',
        'home_wins', 'home_losses', 'away_wins', 'away_losses'
    ]
    
    # Filter to columns that exist
    available_cols = [col for col in export_cols if col in df.columns]
    df_export = df[available_cols].copy()
    
    # Sort by date
    df_export = df_export.sort_values('game_date')
    
    df_export.to_csv(games_file, index=False)
    logger.info(f"Games list saved to {games_file}")
    
    # Summary statistics CSV
    stats_file = os.path.join(config.OUTPUT_DIR, "summary_stats.csv")
    
    stats_rows = []
    
    # Overall stats
    stats_rows.append({
        'Category': 'Overall',
        'Total Games': stats.get('total_games', 0),
        'Home ATS Wins': stats.get('home_ats_wins', 0),
        'Home ATS Losses': stats.get('home_ats_losses', 0),
        'Home ATS Pushes': stats.get('home_ats_pushes', 0),
        'Win Rate (%)': stats.get('home_ats_win_rate', 0.0)
    })
    
    # Monthly breakdown
    if 'monthly_breakdown' in stats:
        month_names = {
            9: 'September', 10: 'October', 11: 'November',
            12: 'December', 1: 'January', 2: 'February'
        }
        for month, month_stats in stats['monthly_breakdown'].items():
            stats_rows.append({
                'Category': f"Month: {month_names.get(month, f'Month {month}')}",
                'Total Games': month_stats.get('total', 0),
                'Home ATS Wins': month_stats.get('covers', 0),
                'Home ATS Losses': month_stats.get('losses', 0),
                'Home ATS Pushes': 0,
                'Win Rate (%)': month_stats.get('win_rate', 0.0)
            })
    
    # Weekly breakdown
    if 'weekly_breakdown' in stats:
        for week, week_stats in sorted(stats['weekly_breakdown'].items()):
            stats_rows.append({
                'Category': f"Week {week}",
                'Total Games': week_stats.get('total', 0),
                'Home ATS Wins': week_stats.get('covers', 0),
                'Home ATS Losses': week_stats.get('losses', 0),
                'Home ATS Pushes': 0,
                'Win Rate (%)': week_stats.get('win_rate', 0.0)
            })
    
    # Playoff status breakdown
    if 'playoff_status_breakdown' in stats:
        for status, status_stats in stats['playoff_status_breakdown'].items():
            stats_rows.append({
                'Category': f"Playoff: {status.replace('_', ' ').title()}",
                'Total Games': status_stats.get('total', 0),
                'Home ATS Wins': status_stats.get('covers', 0),
                'Home ATS Losses': status_stats.get('losses', 0),
                'Home ATS Pushes': 0,
                'Win Rate (%)': status_stats.get('win_rate', 0.0)
            })
    
    stats_df = pd.DataFrame(stats_rows)
    stats_df.to_csv(stats_file, index=False)
    logger.info(f"Summary statistics saved to {stats_file}")


def create_visualizations(df: pd.DataFrame, stats: Dict) -> Dict[str, str]:
    """
    Create visualizations and return file paths.
    
    Args:
        df: DataFrame with qualifying games
        stats: Summary statistics
        
    Returns:
        Dictionary with plot file paths
    """
    logger.info("Creating visualizations...")
    
    plot_files = {}
    
    # Monthly breakdown chart
    if 'monthly_breakdown' in stats and stats['monthly_breakdown']:
        fig, ax = plt.subplots(figsize=(10, 6))
        months = []
        win_rates = []
        totals = []
        
        month_names = {
            9: 'Sep', 10: 'Oct', 11: 'Nov',
            12: 'Dec', 1: 'Jan', 2: 'Feb'
        }
        
        for month in sorted(stats['monthly_breakdown'].keys()):
            month_stats = stats['monthly_breakdown'][month]
            months.append(month_names.get(month, f'M{month}'))
            win_rates.append(month_stats.get('win_rate', 0))
            totals.append(month_stats.get('total', 0))
        
        ax.bar(months, win_rates, color='steelblue', alpha=0.7)
        ax.axhline(y=50, color='r', linestyle='--', label='Break-even (50%)')
        ax.set_xlabel('Month')
        ax.set_ylabel('ATS Win Rate (%)')
        ax.set_title('Home Underdog ATS Win Rate by Month')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add total games as text
        for i, (month, total) in enumerate(zip(months, totals)):
            ax.text(i, win_rates[i] + 1, f'n={total}', ha='center', fontsize=8)
        
        plt.tight_layout()
        monthly_file = os.path.join(config.OUTPUT_DIR, "monthly_breakdown.png")
        plt.savefig(monthly_file, dpi=150, bbox_inches='tight')
        plt.close()
        plot_files['monthly'] = monthly_file
    
    # Weekly breakdown chart
    if 'weekly_breakdown' in stats and stats['weekly_breakdown']:
        fig, ax = plt.subplots(figsize=(12, 6))
        weeks = []
        win_rates = []
        totals = []
        
        for week in sorted(stats['weekly_breakdown'].keys()):
            week_stats = stats['weekly_breakdown'][week]
            weeks.append(week)
            win_rates.append(week_stats.get('win_rate', 0))
            totals.append(week_stats.get('total', 0))
        
        ax.plot(weeks, win_rates, marker='o', linewidth=2, markersize=8, color='steelblue')
        ax.axhline(y=50, color='r', linestyle='--', label='Break-even (50%)')
        ax.set_xlabel('Week of Season')
        ax.set_ylabel('ATS Win Rate (%)')
        ax.set_title('Home Underdog ATS Win Rate by Week')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xticks(weeks)
        
        plt.tight_layout()
        weekly_file = os.path.join(config.OUTPUT_DIR, "weekly_breakdown.png")
        plt.savefig(weekly_file, dpi=150, bbox_inches='tight')
        plt.close()
        plot_files['weekly'] = weekly_file
    
    return plot_files


def generate_html_report(df: pd.DataFrame, stats: Dict) -> None:
    """
    Generate HTML report with analysis results.
    
    Args:
        df: DataFrame with qualifying games
        stats: Summary statistics
    """
    logger.info("Generating HTML report...")
    
    # Create visualizations
    plot_files = create_visualizations(df, stats)
    
    # HTML template
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }
        h2 {
            color: #0066cc;
            margin-top: 30px;
        }
        .summary-box {
            background-color: #f0f8ff;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .stat {
            display: inline-block;
            margin: 10px 20px;
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #0066cc;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #0066cc;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .positive {
            color: #28a745;
            font-weight: bold;
        }
        .negative {
            color: #dc3545;
            font-weight: bold;
        }
        img {
            max-width: 100%;
            height: auto;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <p><strong>{{ subtitle }}</p>
        <p><em>Generated on {{ date }}</em></p>
        
        <div class="summary-box">
            <h2>Overall Summary</h2>
            <div class="stat">
                <div class="stat-value">{{ total_games }}</div>
                <div class="stat-label">Total Games</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ ats_wins }}</div>
                <div class="stat-label">Home ATS Wins</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ ats_losses }}</div>
                <div class="stat-label">Home ATS Losses</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ win_rate }}%</div>
                <div class="stat-label">ATS Win Rate</div>
            </div>
        </div>
        
        {% if monthly_plot %}
        <h2>Monthly Breakdown</h2>
        <img src="{{ monthly_plot }}" alt="Monthly Breakdown">
        {% endif %}
        
        {% if weekly_plot %}
        <h2>Weekly Breakdown</h2>
        <img src="{{ weekly_plot }}" alt="Weekly Breakdown">
        {% endif %}
        
        {% if monthly_stats %}
        <h2>Monthly Statistics</h2>
        <table>
            <tr>
                <th>Month</th>
                <th>Total Games</th>
                <th>Home ATS Wins</th>
                <th>Home ATS Losses</th>
                <th>Win Rate (%)</th>
            </tr>
            {% for month, data in monthly_stats.items() %}
            <tr>
                <td>{{ month }}</td>
                <td>{{ data.total }}</td>
                <td>{{ data.covers }}</td>
                <td>{{ data.losses }}</td>
                <td class="{% if data.win_rate > 50 %}positive{% else %}negative{% endif %}">
                    {{ "%.2f"|format(data.win_rate) }}%
                </td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
        
        {% if weekly_stats %}
        <h2>Weekly Statistics</h2>
        <table>
            <tr>
                <th>Week</th>
                <th>Total Games</th>
                <th>Home ATS Wins</th>
                <th>Home ATS Losses</th>
                <th>Win Rate (%)</th>
            </tr>
            {% for week, data in weekly_stats.items() %}
            <tr>
                <td>Week {{ week }}</td>
                <td>{{ data.total }}</td>
                <td>{{ data.covers }}</td>
                <td>{{ data.losses }}</td>
                <td class="{% if data.win_rate > 50 %}positive{% else %}negative{% endif %}">
                    {{ "%.2f"|format(data.win_rate) }}%
                </td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
        
        {% if playoff_stats %}
        <h2>Playoff Contention Status Breakdown</h2>
        <table>
            <tr>
                <th>Status</th>
                <th>Total Games</th>
                <th>Home ATS Wins</th>
                <th>Home ATS Losses</th>
                <th>Win Rate (%)</th>
            </tr>
            {% for status, data in playoff_stats.items() %}
            <tr>
                <td>{{ status.replace('_', ' ').title() }}</td>
                <td>{{ data.total }}</td>
                <td>{{ data.covers }}</td>
                <td>{{ data.losses }}</td>
                <td class="{% if data.win_rate > 50 %}positive{% else %}negative{% endif %}">
                    {{ "%.2f"|format(data.win_rate) }}%
                </td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
        
        <h2>Conclusion</h2>
        <p>
            {% if win_rate > 52.4 %}
            <strong class="positive">There appears to be value in betting on home underdogs of {{ spread_threshold }}+ points in divisional games.</strong>
            The win rate of {{ win_rate }}% exceeds the break-even point (52.4% at -110 odds).
            {% elif win_rate > 50 %}
            The win rate of {{ win_rate }}% is slightly above break-even but may not provide significant value after accounting for variance.
            {% else %}
            <strong class="negative">There does not appear to be value in this betting strategy.</strong>
            The win rate of {{ win_rate }}% is below the break-even point.
            {% endif %}
        </p>
        
        <p><em>Note: This analysis is for informational purposes only. Past performance does not guarantee future results.</em></p>
    </div>
</body>
</html>
    """
    
    # Prepare data for template
    from datetime import datetime
    
    month_names = {
        9: 'September', 10: 'October', 11: 'November',
        12: 'December', 1: 'January', 2: 'February'
    }
    
    monthly_stats_formatted = {}
    if 'monthly_breakdown' in stats:
        for month, data in stats['monthly_breakdown'].items():
            monthly_stats_formatted[month_names.get(month, f'Month {month}')] = data
    
    weekly_stats_formatted = {}
    if 'weekly_breakdown' in stats:
        for week, data in stats['weekly_breakdown'].items():
            weekly_stats_formatted[week] = data
    
    template = Template(html_template)
    html_content = template.render(
        title=config.REPORT_TITLE,
        subtitle=config.REPORT_SUBTITLE,
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_games=stats.get('total_games', 0),
        ats_wins=stats.get('home_ats_wins', 0),
        ats_losses=stats.get('home_ats_losses', 0),
        win_rate=stats.get('home_ats_win_rate', 0.0),
        spread_threshold=config.SPREAD_THRESHOLD,
        monthly_plot=plot_files.get('monthly', ''),
        weekly_plot=plot_files.get('weekly', ''),
        monthly_stats=monthly_stats_formatted,
        weekly_stats=weekly_stats_formatted,
        playoff_stats=stats.get('playoff_status_breakdown', {})
    )
    
    # Save HTML report
    report_file = os.path.join(config.OUTPUT_DIR, "analysis_report.html")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"HTML report saved to {report_file}")


def generate_all_reports(df: pd.DataFrame, stats: Dict) -> None:
    """
    Generate all reports (CSV and HTML).
    
    Args:
        df: DataFrame with qualifying games
        stats: Summary statistics
    """
    logger.info("Generating all reports...")
    
    generate_csv_reports(df, stats)
    generate_html_report(df, stats)
    
    logger.info("All reports generated successfully")

