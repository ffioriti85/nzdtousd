# -*- coding: utf-8 -*-
"""
Author: AI Assistant
Last updated: 2025-06-27
Version: 0.1.0 (Stable Release) - Adding History Logging Feature with Comparison
Purpose: Main application file for NZD Percentage Converter GUI tool.
         Features: NZD percentage calculation, live USD conversion, 
         percentage persistence, error handling, history logging, and comparison.
Dependencies: tkinter (standard), json (standard), requests (external)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

access_key = "da30bcd9f07ffd758fe1d367c87f036a"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")

class NZDPercentageConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NZD Percentage Converter")
        self.geometry("400x300")  # Increased height for save button
        self.resizable(False, False)
        self.configure(bg="#f9f9f9")
        self._build_ui()
        self._load_last_percentage()
        self.current_calculation = None  # Store current calculation for saving

    def _build_ui(self):
        # Center frame
        frame = ttk.Frame(self, padding=20)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # NZD input
        ttk.Label(frame, text="NZD Amount:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.nzd_var = tk.StringVar()
        nzd_entry = ttk.Entry(frame, textvariable=self.nzd_var, width=20)
        nzd_entry.grid(row=0, column=1, pady=(0, 10))

        # Percentage input
        ttk.Label(frame, text="Percentage (%):").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.percent_var = tk.StringVar()
        percent_entry = ttk.Entry(frame, textvariable=self.percent_var, width=20)
        percent_entry.grid(row=1, column=1, pady=(0, 10))

        # Calculate button
        calc_btn = ttk.Button(frame, text="Calculate", command=self.on_calculate)
        calc_btn.grid(row=2, column=0, columnspan=2, pady=(10, 10))

        # Output labels
        self.nzd_result_label = ttk.Label(frame, text="NZD Result: -")
        self.nzd_result_label.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        self.usd_result_label = ttk.Label(frame, text="USD Result: -")
        self.usd_result_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))

        # Save to History button (initially disabled)
        self.save_btn = ttk.Button(frame, text="Save to History", command=self.on_save_to_history, state="disabled")
        self.save_btn.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        # View History button
        history_btn = ttk.Button(frame, text="View History", command=self.on_view_history)
        history_btn.grid(row=6, column=0, columnspan=2, pady=(5, 0))

    def _load_last_percentage(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    last_percent = data.get("last_percentage", "")
                    # Only set if it's a valid number (not None, not empty string)
                    if isinstance(last_percent, (int, float, str)) and str(last_percent).strip() != "":
                        self.percent_var.set(str(last_percent))
                    else:
                        self.percent_var.set("")
            else:
                self.percent_var.set("")
        except Exception:
            # On any error, just leave the field empty
            self.percent_var.set("")

    def _save_last_percentage(self, percent_value):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"last_percentage": percent_value}, f)
        except Exception as e:
            messagebox.showwarning("Config Error", f"Could not save last percentage.\n{e}")

    def _load_history(self):
        """Load calculation history from file"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def _save_history(self, history_data):
        """Save calculation history to file"""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            messagebox.showerror("History Error", f"Could not save history.\n{e}")

    def on_calculate(self):
        nzd_str = self.nzd_var.get().strip()
        percent_str = self.percent_var.get().strip()
        try:
            nzd_value = float(nzd_str)
            percent_value = float(percent_str)
            if nzd_value < 0 or percent_value < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid, non-negative numbers for NZD and Percentage.")
            self.nzd_result_label.config(text="NZD Result: -")
            self.usd_result_label.config(text="USD Result: -")
            self.save_btn.config(state="disabled")
            self.current_calculation = None
            return

        # Save last-used percentage
        self._save_last_percentage(percent_value)
        
        # Calculate percentage
        nzd_result = nzd_value * (percent_value / 100)
        self.nzd_result_label.config(text=f"NZD Result: {nzd_result:.2f}")
        
        # Store current calculation for potential saving
        self.current_calculation = {
            "nzd_input": nzd_value,
            "percentage": percent_value,
            "nzd_result": nzd_result,
            "usd_result": None,
            "usd_rate": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Fetch USD rate and convert using /convert endpoint
        try:
            response = requests.get(
                "https://api.exchangerate.host/convert",
                params={
                    "from": "NZD",
                    "to": "USD",
                    "amount": nzd_result,
                    "access_key": access_key
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("success", False):
                raise Exception(data.get("error", {}).get("info", "Unknown API error."))
            usd_result = data["result"]
            usd_rate = data["info"]["quote"]
            self.usd_result_label.config(text=f"USD Result: {usd_result:.2f} (Rate: {usd_rate:.4f})")
            
            # Update current calculation with USD data
            self.current_calculation["usd_result"] = usd_result
            self.current_calculation["usd_rate"] = usd_rate
            
        except Exception as e:
            self.usd_result_label.config(text="USD Result: Error")
            messagebox.showerror("API Error", f"Could not fetch USD rate.\n{e}")
        
        # Enable save button after successful calculation
        self.save_btn.config(state="normal")

    def on_save_to_history(self):
        """Save current calculation to history"""
        if not self.current_calculation:
            messagebox.showwarning("No Calculation", "Please calculate a value first.")
            return
        
        try:
            history = self._load_history()
            history.append(self.current_calculation)
            self._save_history(history)
            messagebox.showinfo("Saved", "Calculation saved to history!")
            self.save_btn.config(state="disabled")  # Disable after saving
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save to history.\n{e}")

    def on_view_history(self):
        """Open history viewer window"""
        HistoryViewer(self)

class HistoryViewer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Calculation History")
        self.geometry("800x500")  # Increased width for new column
        self.resizable(True, True)
        self.configure(bg="#f9f9f9")
        self._build_ui()
        self._load_history()

    def _build_ui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Calculation History", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))

        # Treeview for history
        columns = ("Date", "NZD Input", "Percentage", "NZD Result", "USD Result", "Rate", "USD Change %")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("Date", text="Date")
        self.tree.heading("NZD Input", text="NZD Input")
        self.tree.heading("Percentage", text="Percentage")
        self.tree.heading("NZD Result", text="NZD Result")
        self.tree.heading("USD Result", text="USD Result")
        self.tree.heading("Rate", text="USD Rate")
        self.tree.heading("USD Change %", text="USD Change %")
        
        # Column widths
        self.tree.column("Date", width=150)
        self.tree.column("NZD Input", width=80)
        self.tree.column("Percentage", width=80)
        self.tree.column("NZD Result", width=80)
        self.tree.column("USD Result", width=80)
        self.tree.column("Rate", width=80)
        self.tree.column("USD Change %", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # Delete button
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.on_delete_selected)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Clear all button
        clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.on_clear_all)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Close button
        close_btn = ttk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT)

    def _calculate_percentage_change(self, current_usd, previous_usd):
        """Calculate percentage change between two USD values"""
        if previous_usd is None or previous_usd == 0:
            return None
        return ((current_usd - previous_usd) / previous_usd) * 100

    def _load_history(self):
        """Load and display history with comparison"""
        try:
            history = self.parent._load_history()
            self.tree.delete(*self.tree.get_children())  # Clear existing items
            
            # Process history in chronological order for comparison
            sorted_history = sorted(history, key=lambda x: x["timestamp"])
            
            for i, entry in enumerate(sorted_history):
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(entry["timestamp"])
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    date_str = "Unknown"
                
                # Format values
                nzd_input = f"${entry['nzd_input']:.2f}"
                percentage = f"{entry['percentage']}%"
                nzd_result = f"${entry['nzd_result']:.2f}"
                
                if entry.get("usd_result") is not None:
                    usd_result = f"${entry['usd_result']:.2f}"
                    usd_rate = f"{entry['usd_rate']:.4f}"
                    current_usd = entry['usd_result']
                else:
                    usd_result = "Error"
                    usd_rate = "N/A"
                    current_usd = None
                
                # Calculate percentage change
                if i > 0 and current_usd is not None:
                    previous_usd = sorted_history[i-1].get("usd_result")
                    if previous_usd is not None:
                        change_percent = self._calculate_percentage_change(current_usd, previous_usd)
                        if change_percent is not None:
                            change_str = f"{change_percent:+.2f}%"
                            # Color coding will be applied after insertion
                        else:
                            change_str = "N/A"
                    else:
                        change_str = "N/A"
                else:
                    change_str = "N/A"
                
                # Insert item
                item = self.tree.insert("", "end", values=(
                    date_str, nzd_input, percentage, nzd_result, usd_result, usd_rate, change_str
                ))
                
                # Apply color coding only to USD Change % column
                if change_str != "N/A" and current_usd is not None and i > 0:
                    previous_usd = sorted_history[i-1].get("usd_result")
                    if previous_usd is not None:
                        change_percent = self._calculate_percentage_change(current_usd, previous_usd)
                        if change_percent is not None:
                            if change_percent > 0:
                                # Green for increase - use symbols to highlight
                                self.tree.set(item, "USD Change %", f"▲ +{change_percent:.2f}%")
                            elif change_percent < 0:
                                # Red for decrease - use symbols to highlight
                                self.tree.set(item, "USD Change %", f"▼ {change_percent:.2f}%")
                            else:
                                # No change
                                self.tree.set(item, "USD Change %", f"● 0.00%")
            
        except Exception as e:
            messagebox.showerror("History Error", f"Could not load history.\n{e}")

    def on_delete_selected(self):
        """Delete selected history entry"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an entry to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected entry?"):
            try:
                history = self.parent._load_history()
                # Get the index (reverse order since we display newest first)
                index = len(history) - 1 - self.tree.index(selected[0])
                if 0 <= index < len(history):
                    history.pop(index)
                    self.parent._save_history(history)
                    self._load_history()  # Refresh display
                    messagebox.showinfo("Deleted", "Entry deleted successfully!")
            except Exception as e:
                messagebox.showerror("Delete Error", f"Could not delete entry.\n{e}")

    def on_clear_all(self):
        """Clear all history entries"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete ALL history entries?"):
            try:
                self.parent._save_history([])
                self._load_history()  # Refresh display
                messagebox.showinfo("Cleared", "All history entries deleted!")
            except Exception as e:
                messagebox.showerror("Clear Error", f"Could not clear history.\n{e}")

if __name__ == "__main__":
    app = NZDPercentageConverterApp()
    app.mainloop() 