#!/usr/bin/env python3
"""
Quick launcher for the GUI viewer.
Run this to open the GUI and CSV viewer.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Check if outputs exist
    if not Path("outputs/games_list.csv").exists():
        print("No data found. Running analysis first...")
        subprocess.run([sys.executable, "main.py"])
    
    # Open CSV in default application
    csv_path = Path("outputs/games_list.csv").absolute()
    if sys.platform == 'darwin':  # macOS
        subprocess.Popen(['open', str(csv_path)])
    elif sys.platform == 'win32':  # Windows
        os.startfile(str(csv_path))
    else:  # Linux
        subprocess.Popen(['xdg-open', str(csv_path)])
    
    # Launch GUI
    print("Launching GUI viewer...")
    print("CSV file opened in default application.")
    subprocess.run([sys.executable, "gui_viewer.py"])

if __name__ == "__main__":
    main()

