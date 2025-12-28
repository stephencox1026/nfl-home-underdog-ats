"""
Executive-Level GUI for NFL Home Underdog Divisional ATS Analysis
Clean, professional interface organized by season.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import os
try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    try:
        import pyscreenshot as ImageGrab
        HAS_PIL = True
    except ImportError:
        HAS_PIL = False


class ExecutiveNFLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NFL Home Underdog Divisional ATS Analysis")
        self.root.geometry("1600x1000")  # Better for laptop screens
        self.root.minsize(1200, 700)  # Minimum size for readability
        
        # Color scheme: dark blue background, lighter grey boxes, black outlines
        self.colors = {
            'bg': '#1E3A5F',  # Dark blue background
            'card_bg': '#B0B0B0',  # Lighter grey boxes (lightened)
            'card_border': '#000000',  # Black outline
            'header': '#1E3A5F',  # Dark blue headers
            'header_light': '#3B6FA8',  # Medium blue
            'accent': '#3B6FA8',  # Medium blue accent
            'text': '#000000',  # Black text on light grey
            'text_light': '#333333',  # Dark grey text
            'text_secondary': '#666666',  # Medium grey
            'success': '#1B5E20',  # Dark green for >50%
            'failure': '#B71C1C',  # Dark red for <50%
            'neutral': '#9E9E9E',  # Grey
            'border': '#000000',  # Black border
            'hover': '#C0C0C0',  # Lighter grey hover (lightened)
            'shadow': '#000000',  # Black shadow
            'section_bg': '#B0B0B0',  # Lighter grey for sections (lightened)
            'divider': '#000000'  # Black divider
        }
        
        # Clean typography
        if sys.platform == 'darwin':
            base_font = 'SF Pro Text'
        elif sys.platform == 'win32':
            base_font = 'Segoe UI'
        else:
            base_font = 'Ubuntu'
        
        self.fonts = {
            'title': (base_font, 32, 'bold'),  # Increased from 28
            'subtitle': (base_font, 11, 'normal'),
            'season_header': (base_font, 16, 'bold'),
            'stat_value': (base_font, 24, 'bold'),
            'stat_label': (base_font, 9, 'normal'),
            'table_header': (base_font, 10, 'bold'),
            'table_text': (base_font, 9, 'normal'),
            'button': (base_font, 10, 'normal'),
            'meta': (base_font, 9, 'normal')
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg'])
        
        # Load data
        self.games_df = None
        self.load_data()
        
        # Create GUI
        self.create_widgets()
        
        # Auto-export image after GUI is fully loaded
        self.root.after(2000, self.auto_export_image)  # Wait 2 seconds for rendering
        
        # Display all seasons
        if self.games_df is not None and len(self.games_df) > 0:
            self.display_all_seasons()
    
    def load_data(self):
        """Load CSV data file."""
        try:
            games_file = Path("outputs/games_list.csv")
            if games_file.exists():
                self.games_df = pd.read_csv(games_file)
                # Ensure date is datetime
                self.games_df['game_date'] = pd.to_datetime(self.games_df['game_date'])
                # Sort by date
                self.games_df = self.games_df.sort_values('game_date')
            else:
                self.show_error("Data file not found. Please run main.py first.")
        except Exception as e:
            self.show_error(f"Error loading data: {e}")
    
    def show_error(self, message):
        """Display error message."""
        error_label = tk.Label(self.root, text=message, 
                             font=self.fonts['subtitle'], fg=self.colors['failure'],
                             bg=self.colors['bg'])
        error_label.pack(pady=50)
    
    def create_widgets(self):
        """Create the GUI widgets with modern layout."""
        # Main container with modern spacing
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Top bar with title and export
        self.create_top_bar(self.main_container)
        
        # Create scrollable content area
        self.create_scrollable_view(self.main_container)
    
    def create_top_bar(self, parent):
        """Create top bar with title and actions - no box, matches background."""
        top_bar = tk.Frame(parent, bg=self.colors['bg'], height=100)
        top_bar.pack(fill=tk.X, side=tk.TOP, padx=48, pady=20)
        top_bar.pack_propagate(False)
        
        # Inner container with padding
        inner = tk.Frame(top_bar, bg=self.colors['bg'])
        inner.pack(fill=tk.BOTH, expand=True, padx=0, pady=16)
        
        # Left side - Title
        title_container = tk.Frame(inner, bg=self.colors['bg'])
        title_container.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(
            title_container,
            text="NFL Home Underdog Analysis",
            font=self.fonts['title'],
            fg='white',  # White text on dark blue background
            bg=self.colors['bg']
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            title_container,
            text="Divisional Games • Home Underdogs 3.5+ Points",
            font=self.fonts['subtitle'],
            fg='#CCCCCC',  # Light grey text on dark blue
            bg=self.colors['bg']
        )
        subtitle_label.pack(anchor=tk.W, pady=(4, 0))
        
        # Right side - Export button with black text
        if HAS_PIL:
            export_btn = tk.Button(
                inner,
                text="Export Image",
                font=self.fonts['button'],
                fg='#000000',  # Black text
                bg=self.colors['card_bg'],  # Light grey background
                relief=tk.SOLID,
                bd=1,
                highlightbackground=self.colors['card_border'],
                highlightthickness=1,
                cursor="hand2",
                padx=20,
                pady=8,
                command=self.export_as_image,
                activebackground=self.colors['hover'],
                activeforeground='#000000'  # Black text on hover
            )
            export_btn.pack(side=tk.RIGHT, padx=(20, 0))
    
    def create_export_button(self, parent):
        """Create export button in title area."""
        if not HAS_PIL:
            return
        
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        export_btn = tk.Button(
            button_frame,
            text="📷 Export as Image",
            font=self.fonts['button'],
            fg='white',
            bg=self.colors['header_light'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.export_as_image
        )
        export_btn.pack(side=tk.RIGHT)
    
    def create_scrollable_view(self, parent):
        """Create modern scrollable canvas for all seasons."""
        # Create frame with scrollbar
        scroll_frame = tk.Frame(parent, bg=self.colors['bg'])
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar with modern styling
        canvas = tk.Canvas(scroll_frame, bg=self.colors['bg'], highlightthickness=0, 
                          borderwidth=0)
        v_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        # Scrollable frame inside canvas with padding
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        # Configure canvas scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", 
                           width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack scrollbar and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Update canvas width when window resizes
        def update_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas.find_all()[0], width=canvas_width)
        
        canvas.bind('<Configure>', update_canvas_width)
        
        self.canvas = canvas
    
    def create_season_section(self, parent, season):
        """Create modern season section with card design."""
        # Main season container with reduced spacing
        season_container = tk.Frame(parent, bg=self.colors['bg'])
        season_container.pack(fill=tk.X, pady=(0, 16), padx=48)  # Reduced from 24 to 16
        
        # Add ad box for 2024 season
        if season == 2024:
            ad_frame = tk.Frame(season_container, bg=self.colors['card_bg'], 
                               relief=tk.SOLID, bd=1,
                               highlightbackground=self.colors['card_border'],
                               highlightthickness=1)
            ad_frame.pack(fill=tk.X, pady=(0, 16))
            
            # Title - centered and larger
            ad_title = "🎬 Coming 2026: The Richard Sondgroth Story 🎬"
            title_label = tk.Label(
                ad_frame,
                text=ad_title,
                font=(self.fonts['subtitle'][0], self.fonts['subtitle'][1] + 9, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['card_bg'],
                justify=tk.CENTER
            )
            title_label.pack(padx=20, pady=(12, 8), anchor=tk.CENTER)
            
            # Body text - larger and left-aligned
            ad_body = "A good-hearted Texan who's got two passions: the perfect pair of kicks and the best BBQ in the Lone Star State. " \
                      "When he's not hunting down rare sneakers or perfecting his brisket, he's just being an all-around great guy. " \
                      "But behind the scenes, there's a complicated love story unfolding with a man who keeps him on his toes - " \
                      "a relationship full of passion, late-night conversations, and the kind of drama that makes life interesting. " \
                      "This one's for you, Richard! 🤠👟🍖💕"
            
            body_label = tk.Label(
                ad_frame,
                text=ad_body,
                font=(self.fonts['subtitle'][0], self.fonts['subtitle'][1] + 5, 'normal'),
                fg=self.colors['text'],
                bg=self.colors['card_bg'],
                justify=tk.LEFT,
                wraplength=1400  # Increased to stretch across whole box
            )
            body_label.pack(padx=20, pady=(0, 12), fill=tk.X, anchor=tk.W)
        
        # Light grey card with thin black outline
        summary_frame = tk.Frame(season_container, bg=self.colors['card_bg'], 
                                 relief=tk.SOLID, bd=1,
                                 highlightbackground=self.colors['card_border'],
                                 highlightthickness=1)
        summary_frame.pack(fill=tk.X)
        
        # Inner content with reduced padding to decrease box height
        summary_inner = tk.Frame(summary_frame, bg=self.colors['card_bg'])
        summary_inner.pack(fill=tk.BOTH, padx=32, pady=12)  # Reduced from 16 to 12
        
        # Container for games table (hidden by default)
        games_container = tk.Frame(season_container, bg=self.colors['card_bg'])
        
        return summary_inner, games_container, season_container
    
    def create_season_summary(self, parent, season_data):
        """Create season summary display."""
        if season_data is None or len(season_data) == 0:
            no_data_label = tk.Label(
                parent,
                text="No data available for this season",
                font=self.fonts['subtitle'],
                fg=self.colors['text_light'],
                bg=self.colors['card_bg']
            )
            no_data_label.pack()
            return
        
        # Calculate statistics
        total_games = len(season_data)
        covers = season_data['home_covered'].sum()
        losses = (~season_data['home_covered']).sum()
        pushes = (season_data.get('home_pushed', pd.Series([False] * len(season_data)))).sum() if 'home_pushed' in season_data.columns else 0
        
        games_with_result = covers + losses
        win_rate = (covers / games_with_result * 100) if games_with_result > 0 else 0
        
        # Determine profitability
        is_profitable = win_rate > 52.4
        
        # Modern season header with reduced spacing
        header_container = tk.Frame(parent, bg=self.colors['card_bg'])
        header_container.pack(fill=tk.X, pady=(0, 10))  # Reduced from 12 to 10
        
        # Left side - Season title
        title_side = tk.Frame(header_container, bg=self.colors['card_bg'])
        title_side.pack(side=tk.LEFT, fill=tk.Y)
        
        season_label = tk.Label(
            title_side,
            text=f"{int(season_data['season'].iloc[0])} Season",
            font=self.fonts['season_header'],
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        )
        season_label.pack(anchor=tk.W)
        
        # Right side - Expand/Collapse button with black text
        expand_btn = tk.Button(
            header_container,
            text="View Games ▼",
            font=self.fonts['button'],
            fg='#000000',  # Black text
            bg=self.colors['card_bg'],
            relief=tk.SOLID,
            bd=1,
            highlightbackground=self.colors['card_border'],
            highlightthickness=1,
            cursor="hand2",
            padx=16,
            pady=6,
            command=lambda: self.toggle_games(season_data['season'].iloc[0]),
            activebackground=self.colors['hover'],
            activeforeground='#000000'  # Black text on hover
        )
        expand_btn.pack(side=tk.RIGHT)
        
        # Store button reference
        self.expand_buttons = getattr(self, 'expand_buttons', {})
        self.expand_buttons[int(season_data['season'].iloc[0])] = expand_btn
        
        # Modern stats grid with minimized spacing
        stats_container = tk.Frame(parent, bg=self.colors['card_bg'])
        stats_container.pack(fill=tk.X, pady=(0, 0))
        
        # Create stat cards with conditional formatting for win rate and status
        # Win rate: >50% green, <50% red
        win_rate_color = self.colors['success'] if win_rate > 50 else self.colors['failure']
        # Status: >50% green, <50% red
        status_color = self.colors['success'] if win_rate > 50 else self.colors['failure']
        
        stats = [
            ("Total Games", str(total_games), self.colors['text']),
            ("ATS Record", f"{int(covers)}-{int(losses)}" + (f"-{int(pushes)}" if pushes > 0 else ""), 
             self.colors['text']),
            ("Win Rate", f"{win_rate:.2f}%", win_rate_color),
            ("Status", "Profitable" if is_profitable else "Not Profitable", status_color)
        ]
        
        for i, (label, value, color) in enumerate(stats):
            padx_right = 48 if i < len(stats) - 1 else 0
            self.create_stat_card(stats_container, label, value, color, 
                                side=tk.LEFT, padx=(0, padx_right))
    
    def create_stat_card(self, parent, label, value, color, side=tk.LEFT, padx=0):
        """Create modern stat card with better visual hierarchy."""
        card_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        card_frame.pack(side=side, padx=padx)
        
        # Value (large, prominent)
        value_label = tk.Label(
            card_frame,
            text=value,
            font=self.fonts['stat_value'],
            fg=color,
            bg=self.colors['card_bg']
        )
        value_label.pack(anchor=tk.W)
        
        # Label (small, subtle)
        label_label = tk.Label(
            card_frame,
            text=label.upper(),
            font=self.fonts['stat_label'],
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        label_label.pack(anchor=tk.W, pady=(4, 0))
    
    def create_games_table(self, parent, season_num):
        """Create executive-style games table - clean, no scrolling, shows all games."""
        table_container = tk.Frame(parent, bg=self.colors['card_bg'], 
                                   relief=tk.SOLID, bd=1,
                                   highlightbackground=self.colors['card_border'],
                                   highlightthickness=1)
        table_container.pack(fill=tk.X, pady=(16, 0), padx=0)
        
        # Clean header with minimal styling
        header_frame = tk.Frame(table_container, bg=self.colors['card_bg'], height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="Game Details",
            font=(self.fonts['table_header'][0], self.fonts['table_header'][1] + 1, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        )
        header_label.pack(side=tk.LEFT, padx=24, pady=10)
        
        # Table frame with clean padding
        table_frame = tk.Frame(table_container, bg=self.colors['card_bg'])
        table_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 20), expand=True)
        
        # Treeview - no height limit, no scrolling
        columns = ('visiting_team', 'home_team', 'spread', 'final_score', 'ats_result', 'home_cover')
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            style="Executive.Treeview"
        )
        
        # Column configuration with better widths
        column_configs = {
            'visiting_team': ('Visiting Team', 160),
            'home_team': ('Home Team', 160),
            'spread': ('Spread', 90),
            'final_score': ('Final Score', 130),
            'ats_result': ('ATS Result', 110),
            'home_cover': ('Cover', 80)
        }
        
        for col, (heading, width) in column_configs.items():
            tree.heading(col, text=heading, anchor=tk.CENTER)
            tree.column(col, width=width, anchor=tk.CENTER, minwidth=width)
        
        # Pack tree - no scrollbar
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Executive-style table styling
        style = ttk.Style()
        
        # Base treeview style - clean executive look
        style.configure("Executive.Treeview", 
                       background='#E0E0E0',  # Darker grey default (will be overridden by tags)
                       foreground=self.colors['text'],
                       fieldbackground='#E0E0E0',
                       rowheight=32,  # Reduced row height to see all results
                       font=(self.fonts['table_text'][0], self.fonts['table_text'][1] + 1),  # Slightly larger font
                       borderwidth=0,
                       relief=tk.FLAT,
                       padding=(5, 6))  # Reduced internal padding
        
        # Header style
        style.configure("Executive.Treeview.Heading",
                       background=self.colors['card_bg'],
                       foreground=self.colors['text'],
                       font=(self.fonts['table_header'][0], self.fonts['table_header'][1] + 1, 'bold'),
                       relief=tk.FLAT,
                       borderwidth=0,
                       padding=(10, 12))
        
        # Remove selection highlighting for cleaner look
        style.map("Executive.Treeview",
                 background=[('selected', '#B0B0B0')],  # Darker grey on selection
                 foreground=[('selected', self.colors['text'])])
        
        return tree
    
    def display_all_seasons(self):
        """Display all seasons one after another."""
        if self.games_df is None or len(self.games_df) == 0:
            return
        
        # Initialize expand buttons dict and games containers dict
        self.expand_buttons = {}
        self.games_containers = {}
        self.games_trees = {}
        self.games_visible = {}  # Track visibility state
        
        # Get all seasons sorted (newest first)
        seasons = sorted(self.games_df['season'].dropna().unique().astype(int), reverse=True)
        
        for season in seasons:
            season_data = self.games_df[self.games_df['season'] == season].copy()
            
            # Create season section
            summary_inner, games_container, season_container = self.create_season_section(
                self.scrollable_frame, season
            )
            
            # Create and populate summary
            self.create_season_summary(summary_inner, season_data)
            
            # Create games table (but don't show it yet)
            tree = self.create_games_table(games_container, season)
            
            # Populate games table
            self.populate_games_table(tree, season_data)
            
            # Store references
            self.games_containers[season] = games_container
            self.games_trees[season] = tree
            self.games_visible[season] = False  # Default to hidden
        
        # Update canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def toggle_games(self, season):
        """Toggle visibility of games table for a season."""
        season = int(season)
        container = self.games_containers.get(season)
        button = self.expand_buttons.get(season)
        
        if container is None or button is None:
            return
        
        is_visible = self.games_visible.get(season, False)
        
        if is_visible:
            # Hide games
            container.pack_forget()
            button.config(text="View Games ▼", fg='#000000')  # Black text
            self.games_visible[season] = False
        else:
            # Show games
            parent_container = container.master
            container.pack(fill=tk.X, pady=(16, 0))
            button.config(text="Hide Games ▲", fg='#000000')  # Black text
            self.games_visible[season] = True
        
        # Update canvas scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def populate_games_table(self, tree, season_data):
        """Populate games table with season data."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        if season_data is None or len(season_data) == 0:
            return
        
        # Sort by date
        season_data = season_data.sort_values('game_date')
        
        # Add rows with alternating background colors for readability
        row_num = 0
        for idx, row in season_data.iterrows():
            # Visiting team (away team)
            visiting_team = str(row.get('away_team_normalized', ''))
            
            # Home team
            home_team = str(row.get('home_team_normalized', ''))
            
            # Spread
            spread_val = row.get('home_spread', None)
            if pd.notna(spread_val):
                spread = f"+{spread_val:.1f}" if spread_val > 0 else f"{spread_val:.1f}"
            else:
                spread = "N/A"
            
            # Final score (Home - Away format)
            home_score = row.get('home_score', row.get('score_home', None))
            away_score = row.get('away_score', row.get('score_away', None))
            if pd.notna(home_score) and pd.notna(away_score):
                final_score = f"{int(home_score)} - {int(away_score)}"
            else:
                final_score = "N/A"
            
            # ATS Result
            ats_result = str(row.get('ats_result', ''))
            
            # Home Cover
            home_covered = bool(row.get('home_covered', False)) if pd.notna(row.get('home_covered', False)) else False
            home_cover_text = "Yes" if home_covered else "No"
            
            # Insert row
            item = tree.insert('', tk.END, values=(
                visiting_team,
                home_team,
                spread,
                final_score,
                ats_result,
                home_cover_text
            ))
            
            # Alternating row colors for better readability
            tags = []
            if row_num % 2 == 0:
                tags.append('even_row')
            else:
                tags.append('odd_row')
            
            # Color code based on ATS result
            if home_covered:
                tree.set(item, 'ats_result', 'Cover')
                tags.append('cover')
            elif ats_result == 'Push':
                tree.set(item, 'ats_result', 'Push')
                tags.append('push')
            else:
                tree.set(item, 'ats_result', 'Loss')
                tags.append('loss')
            
            # Apply tags
            tree.item(item, tags=tuple(tags))
            row_num += 1
        
        # Configure tags for color coding and alternating rows (darker)
        tree.tag_configure('even_row', background='#D0D0D0')  # Darker grey for even rows
        tree.tag_configure('odd_row', background='#C8C8C8')  # Darker grey for odd rows
        tree.tag_configure('cover', foreground=self.colors['success'])  # Dark green for covers
        tree.tag_configure('loss', foreground=self.colors['failure'])  # Dark red for losses
        tree.tag_configure('push', foreground=self.colors['neutral'])  # Grey for pushes
    
    def auto_export_image(self):
        """Automatically export the GUI window as an image to Documents folder."""
        self.export_as_image(silent=True)
    
    def export_as_image(self, silent=False):
        """Export the GUI window as an image to Documents folder."""
        if not HAS_PIL:
            if not silent:
                messagebox.showerror("Export Error", 
                    "PIL/Pillow or pyscreenshot is required for image export.\n"
                    "Install with: pip install pillow")
            return
        
        try:
            # Get Documents folder path
            if sys.platform == 'darwin':  # macOS
                documents_path = Path.home() / "Documents"
            elif sys.platform == 'win32':  # Windows
                documents_path = Path(os.path.expanduser("~/Documents"))
            else:  # Linux
                documents_path = Path.home() / "Documents"
            
            # Create Documents folder if it doesn't exist
            documents_path.mkdir(parents=True, exist_ok=True)
            
            # Set filename
            filename = documents_path / "NFL Home Dog Analysis.png"
            
            # Bring window to front and ensure it's fully rendered
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.update_idletasks()
            self.root.update()
            
            # Wait for rendering
            import time
            time.sleep(0.5)
            
            # Get the main container widget position and size (content area only)
            self.root.update_idletasks()
            self.main_container.update_idletasks()
            
            # Get screen coordinates of the main container
            x = self.main_container.winfo_rootx()
            y = self.main_container.winfo_rooty()
            width = self.main_container.winfo_width()
            height = self.main_container.winfo_height()
            
            # Capture the content area
            img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            
            # Reset window attributes
            self.root.attributes('-topmost', False)
            
            # Save the image
            img.save(str(filename))
            
            if not silent:
                messagebox.showinfo("Export Successful", 
                    f"Image saved successfully to:\n{filename}")
            else:
                print(f"Image auto-saved to: {filename}")
            
        except Exception as e:
            if not silent:
                messagebox.showerror("Export Error", 
                    f"Failed to export image:\n{str(e)}")
            else:
                print(f"Auto-export error: {str(e)}")


def main():
    root = tk.Tk()
    app = ExecutiveNFLGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

