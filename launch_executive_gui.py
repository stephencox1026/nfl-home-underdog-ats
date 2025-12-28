#!/usr/bin/env python3
"""
Launcher for the Executive-Level GUI.
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Check if data exists
    if not Path("outputs/games_list.csv").exists():
        print("No data found. Running analysis first...")
        subprocess.run([sys.executable, "main.py"])
    
    # Launch executive GUI
    print("Launching Executive-Level GUI...")
    subprocess.run([sys.executable, "executive_gui.py"])

if __name__ == "__main__":
    main()

