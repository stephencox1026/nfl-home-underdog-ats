"""
GUI viewer for NFL Home Underdog Divisional ATS Analysis results.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from pathlib import Path

class NFLATSAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NFL Home Underdog Divisional ATS Analysis")
        self.root.geometry("1200x800")
        
        # Load data
        self.games_df = None
        self.stats_df = None
        self.load_data()
        
        # Create GUI
        self.create_widgets()
        
    def load_data(self):
        """Load CSV data files."""
        try:
            games_file = Path("outputs/games_list.csv")
            stats_file = Path("outputs/summary_stats.csv")
            
            if games_file.exists():
                self.games_df = pd.read_csv(games_file)
            else:
                messagebox.showwarning("File Not Found", 
                    f"Could not find {games_file}\nPlease run main.py first to generate data.")
                return
            
            if stats_file.exists():
                self.stats_df = pd.read_csv(stats_file)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {e}")
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary Tab
        self.create_summary_tab(notebook)
        
        # Games List Tab
        self.create_games_tab(notebook)
        
        # Statistics Tab
        self.create_stats_tab(notebook)
        
        # Menu bar
        self.create_menu()
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open CSV...", command=self.open_csv_file)
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_summary_tab(self, notebook):
        """Create summary statistics tab."""
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Summary")
        
        # Title
        title_label = tk.Label(summary_frame, text="NFL Home Underdog Divisional ATS Analysis", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        if self.games_df is not None and len(self.games_df) > 0:
            # Calculate summary stats
            total_games = len(self.games_df)
            covers = self.games_df['home_covered'].sum()
            losses = (~self.games_df['home_covered']).sum()
            pushes = self.games_df['home_pushed'].sum() if 'home_pushed' in self.games_df.columns else 0
            win_rate = (covers / (covers + losses) * 100) if (covers + losses) > 0 else 0
            
            # Summary stats frame
            stats_frame = ttk.LabelFrame(summary_frame, text="Overall Statistics", padding=20)
            stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Stats grid
            stats_text = f"""
Total Qualifying Games: {total_games}
Home ATS Wins: {int(covers)}
Home ATS Losses: {int(losses)}
Home ATS Pushes: {int(pushes)}
ATS Win Rate: {win_rate:.2f}%
            """
            
            stats_label = tk.Label(stats_frame, text=stats_text.strip(), 
                                  font=("Arial", 12), justify=tk.LEFT)
            stats_label.pack(anchor=tk.W)
            
            # Value assessment
            value_frame = ttk.LabelFrame(summary_frame, text="Betting Value Assessment", padding=20)
            value_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            if win_rate > 52.4:
                value_text = "✓ There appears to be VALUE in this betting strategy\n" \
                           f"(Win rate of {win_rate:.2f}% exceeds break-even point of 52.4% at -110 odds)"
                color = "green"
            elif win_rate > 50:
                value_text = f"~ Win rate of {win_rate:.2f}% is slightly above break-even\n" \
                           "(May not provide significant value after accounting for variance)"
                color = "orange"
            else:
                value_text = "✗ There does NOT appear to be value in this betting strategy\n" \
                           f"(Win rate of {win_rate:.2f}% is below break-even point)"
                color = "red"
            
            value_label = tk.Label(value_frame, text=value_text, 
                                   font=("Arial", 11), fg=color, justify=tk.LEFT)
            value_label.pack(anchor=tk.W)
            
            # Date range
            if 'game_date' in self.games_df.columns:
                date_range = f"Date Range: {self.games_df['game_date'].min()} to {self.games_df['game_date'].max()}"
                date_label = tk.Label(summary_frame, text=date_range, font=("Arial", 10))
                date_label.pack(pady=5)
        else:
            no_data_label = tk.Label(summary_frame, text="No data available. Please run main.py first.", 
                                     font=("Arial", 12))
            no_data_label.pack(pady=50)
    
    def create_games_tab(self, notebook):
        """Create games list tab with table."""
        games_frame = ttk.Frame(notebook)
        notebook.add(games_frame, text="Games List")
        
        if self.games_df is not None and len(self.games_df) > 0:
            # Filter frame
            filter_frame = ttk.Frame(games_frame)
            filter_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(filter_frame, text="Filter by Season:").pack(side=tk.LEFT, padx=5)
            self.season_var = tk.StringVar(value="All")
            season_combo = ttk.Combobox(filter_frame, textvariable=self.season_var, 
                                        values=["All"] + sorted(self.games_df['season'].dropna().unique().astype(int).tolist()),
                                        state="readonly", width=10)
            season_combo.pack(side=tk.LEFT, padx=5)
            season_combo.bind("<<ComboboxSelected>>", self.filter_games)
            
            # Treeview for table
            tree_frame = ttk.Frame(games_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
            
            # Treeview
            columns = ['game_date', 'season', 'week', 'home_team_normalized', 'away_team_normalized', 
                      'home_score', 'away_score', 'home_spread', 'ats_result', 'temperature', 'wind_speed']
            self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                    yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Configure scrollbars
            v_scrollbar.config(command=self.tree.yview)
            h_scrollbar.config(command=self.tree.xview)
            
            # Column headings
            column_names = {
                'game_date': 'Date',
                'season': 'Season',
                'week': 'Week',
                'home_team_normalized': 'Home Team',
                'away_team_normalized': 'Away Team',
                'home_score': 'Home Score',
                'away_score': 'Away Score',
                'home_spread': 'Spread',
                'ats_result': 'ATS Result',
                'temperature': 'Temp (°F)',
                'wind_speed': 'Wind (mph)'
            }
            
            for col in columns:
                self.tree.heading(col, text=column_names.get(col, col))
                self.tree.column(col, width=100, anchor=tk.CENTER)
            
            # Pack scrollbars and tree
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Populate data
            self.populate_games_table()
        else:
            no_data_label = tk.Label(games_frame, text="No data available. Please run main.py first.", 
                                     font=("Arial", 12))
            no_data_label.pack(pady=50)
    
    def populate_games_table(self, filtered_df=None):
        """Populate the games table."""
        if filtered_df is None:
            filtered_df = self.games_df
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add rows
        for idx, row in filtered_df.iterrows():
            values = [
                str(row.get('game_date', '')),
                str(int(row.get('season', ''))) if pd.notna(row.get('season')) else '',
                str(int(row.get('week', ''))) if pd.notna(row.get('week')) else '',
                str(row.get('home_team_normalized', '')),
                str(row.get('away_team_normalized', '')),
                str(int(row.get('home_score', ''))) if pd.notna(row.get('home_score')) else '',
                str(int(row.get('away_score', ''))) if pd.notna(row.get('away_score')) else '',
                f"{row.get('home_spread', ''):.1f}" if pd.notna(row.get('home_spread')) else '',
                str(row.get('ats_result', '')),
                f"{row.get('temperature', ''):.0f}" if pd.notna(row.get('temperature')) else '',
                f"{row.get('wind_speed', ''):.0f}" if pd.notna(row.get('wind_speed')) else ''
            ]
            self.tree.insert('', tk.END, values=values)
    
    def filter_games(self, event=None):
        """Filter games by season."""
        if self.games_df is None:
            return
        
        season = self.season_var.get()
        if season == "All":
            self.populate_games_table()
        else:
            filtered = self.games_df[self.games_df['season'] == int(season)]
            self.populate_games_table(filtered)
    
    def create_stats_tab(self, notebook):
        """Create statistics breakdown tab."""
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        
        if self.stats_df is not None and len(self.stats_df) > 0:
            # Treeview for stats
            tree_frame = ttk.Frame(stats_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
            
            columns = list(self.stats_df.columns)
            stats_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                     yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            v_scrollbar.config(command=stats_tree.yview)
            h_scrollbar.config(command=stats_tree.xview)
            
            for col in columns:
                stats_tree.heading(col, text=col.replace('_', ' ').title())
                stats_tree.column(col, width=150, anchor=tk.CENTER)
            
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Populate stats
            for idx, row in self.stats_df.iterrows():
                values = [str(row[col]) for col in columns]
                stats_tree.insert('', tk.END, values=values)
        else:
            no_data_label = tk.Label(stats_frame, text="No statistics available.", 
                                     font=("Arial", 12))
            no_data_label.pack(pady=50)
    
    def open_csv_file(self):
        """Open CSV file with system default application."""
        csv_file = filedialog.askopenfilename(
            initialdir="outputs",
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if csv_file:
            import subprocess
            import platform
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', csv_file])
            elif platform.system() == 'Windows':
                os.startfile(csv_file)
            else:  # Linux
                subprocess.call(['xdg-open', csv_file])
    
    def export_results(self):
        """Export results to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path and self.games_df is not None:
            self.games_df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Results exported to {file_path}")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """NFL Home Underdog Divisional ATS Analysis

Analyzes NFL divisional games from 2014-2024 where the home team 
was an underdog by 3.5+ points to determine betting value.

Data Sources:
- nflfastR (nfl-data-py) for historical game data
- Spreadspoke.com as fallback

Version: 1.0
"""
        messagebox.showinfo("About", about_text)


def main():
    root = tk.Tk()
    app = NFLATSAnalysisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

