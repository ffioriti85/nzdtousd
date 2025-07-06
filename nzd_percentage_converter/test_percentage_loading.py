#!/usr/bin/env python3
"""
Test script to verify percentage loading from history.json
"""

import json
import os

def load_history():
    """Load calculation history from file"""
    history_file = "history.json"
    try:
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception:
        return []

def load_last_percentage():
    """Test the new percentage loading logic"""
    try:
        history = load_history()
        if history:
            # Get the latest entry (most recent) and extract its percentage
            latest_entry = history[-1]
            last_percent = latest_entry.get("percentage", 0)
            print(f"Latest percentage from history: {last_percent}")
            return last_percent
        else:
            # No history exists, set to 0 for first execution
            print("No history found, defaulting to 0")
            return 0
    except Exception as e:
        print(f"Error loading percentage: {e}")
        return 0

if __name__ == "__main__":
    print("Testing percentage loading from history.json...")
    percentage = load_last_percentage()
    print(f"Final percentage value: {percentage}") 