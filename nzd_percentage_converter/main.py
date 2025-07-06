# -*- coding: utf-8 -*-
"""
Author: AI Assistant
Last updated: 2025-06-27
Version: 0.3.0 (Stable Release) - Google Sheets Integration
Purpose: Main application file for NZD Percentage Converter GUI tool.
         Features: NZD percentage calculation, live USD conversion, 
         percentage persistence, error handling, history logging, comparison,
         and Google Sheets cloud storage integration.
Dependencies: tkinter (standard), json (standard), requests (external), google-api-python-client (external)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
import sys
from datetime import datetime
from google_sheets import GoogleSheetsManager

access_key = "da30bcd9f07ffd758fe1d367c87f036a"

# Handle file paths for both development and executable environments
def get_app_directory():
    """Get the directory where the application is running"""
    if getattr(sys, 'frozen', False):
        # Running as executable
        return os.path.dirname(sys.executable)
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))

# Set file paths
APP_DIR = get_app_directory()
HISTORY_FILE = os.path.join(APP_DIR, "history.json")

# Ensure app directory exists
os.makedirs(APP_DIR, exist_ok=True)

# Debug information (can be removed in production)
print(f"App Directory: {APP_DIR}")
print(f"History File: {HISTORY_FILE}")

class NZDPercentageConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NZD Percentage Converter")
        self.geometry("500x450")  # Increased size for better field display and Google Sheets buttons
        self.resizable(False, False)
        self.configure(bg="#f9f9f9")
        
        # Initialize Google Sheets manager first
        self.sheets_manager = GoogleSheetsManager(APP_DIR)
        
        self._build_ui()
        self._load_last_percentage()
        self.current_calculation = None  # Store current calculation for saving
        
        # Auto-check Google Sheets setup on startup
        self._auto_check_sheets_setup()

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

        # Calculate & Save button
        calc_btn = ttk.Button(frame, text="Calculate & Save", command=self.on_calculate)
        calc_btn.grid(row=2, column=0, columnspan=2, pady=(10, 10))

        # Output labels
        self.nzd_result_label = ttk.Label(frame, text="NZD Result: -")
        self.nzd_result_label.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        self.usd_result_label = ttk.Label(frame, text="USD Result: -")
        self.usd_result_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))



        # View History button
        history_btn = ttk.Button(frame, text="View History", command=self.on_view_history)
        history_btn.grid(row=6, column=0, columnspan=2, pady=(5, 0))

        # Google Sheets section
        sheets_frame = ttk.LabelFrame(frame, text="Google Sheets", padding=10)
        sheets_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        # Setup Google Sheets button
        self.setup_sheets_btn = ttk.Button(sheets_frame, text="Setup Google Sheets", command=self.on_setup_sheets)
        self.setup_sheets_btn.pack(fill="x", pady=(0, 5))

        # Open Sheets button (initially disabled)
        self.open_sheets_btn = ttk.Button(sheets_frame, text="Open Google Sheets", command=self.on_open_sheets, state="disabled")
        self.open_sheets_btn.pack(fill="x")

        # Update Google Sheets button states
        self._update_sheets_buttons()

    def _load_last_percentage(self):
        try:
            history = self._load_history()
            if history:
                # Get the latest entry (most recent) and extract its percentage
                latest_entry = history[-1]
                last_percent = latest_entry.get("percentage", 0)
                # Set the percentage value (default to 0 if not found)
                self.percent_var.set(str(last_percent))
            else:
                # No history exists, set to 0 for first execution
                self.percent_var.set("0")
        except Exception:
            # On any error, set to 0
            self.percent_var.set("0")



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
            self.current_calculation = None
            return

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
        
        # Update Google Sheets buttons
        self._update_sheets_buttons()
        
        # Automatically save the calculation
        self._auto_save_calculation()

    def _auto_save_calculation(self):
        """Automatically save the current calculation to local history and Google Sheets"""
        if not self.current_calculation:
            return
        
        # Save to local history first
        local_success = False
        try:
            history = self._load_history()
            history.append(self.current_calculation)
            self._save_history(history)
            local_success = True
        except Exception as e:
            messagebox.showerror("Local Save Error", f"Could not save to local history.\n{e}")
            return
        
        # Try to save to Google Sheets if configured
        sheets_success = False
        sheets_message = ""
        if self.sheets_manager.is_configured() and self.sheets_manager.check_spreadsheet_access():
            try:
                # Calculate percentage change by comparing with previous entry in Google Sheets
                usd_change_percent = ''
                current_usd = self.current_calculation.get('usd_result')
                
                if current_usd is not None:
                    # Get the last entry from Google Sheets to calculate percentage change
                    previous_usd = self.sheets_manager.get_last_usd_result()
                    if previous_usd is not None:
                        change_percent = self._calculate_percentage_change(current_usd, previous_usd)
                        if change_percent is not None:
                            # Store as raw float number for Google Sheets (not string)
                            usd_change_percent = change_percent
                        else:
                            usd_change_percent = "N/A"
                    else:
                        usd_change_percent = "N/A"
                
                # Prepare data for upload
                upload_data = {
                    'timestamp': self.current_calculation['timestamp'],
                    'nzd_input': self.current_calculation['nzd_input'],
                    'percentage': self.current_calculation['percentage'],
                    'nzd_result': self.current_calculation['nzd_result'],
                    'usd_result': self.current_calculation.get('usd_result', ''),
                    'usd_rate': self.current_calculation.get('usd_rate', ''),
                    'usd_change_percent': usd_change_percent,
                    'notes': ''
                }
                
                success, message = self.sheets_manager.upload_calculation(upload_data)
                if success:
                    sheets_success = True
                    sheets_message = f"\nGoogle Sheets: {message}"
                else:
                    sheets_message = f"\nGoogle Sheets: {message}"
            except Exception as e:
                sheets_message = f"\nGoogle Sheets: Error - {e}"
        else:
            sheets_message = "\nGoogle Sheets: Not configured"
        
        # Show appropriate success message
        if local_success and sheets_success:
            messagebox.showinfo("Saved", f"Calculation saved to history and Google Sheets!{sheets_message}")
        elif local_success:
            messagebox.showinfo("Saved", f"Calculation saved to local history.{sheets_message}")

    def on_view_history(self):
        """Open history viewer window"""
        HistoryViewer(self)

    def _auto_check_sheets_setup(self):
        """Automatically check Google Sheets setup on app startup"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.sheets_manager.credentials_file):
                return  # No credentials, user needs to set up manually
            
            # Check if we have a saved spreadsheet ID
            if not self.sheets_manager.spreadsheet_id:
                return  # No spreadsheet ID saved, user needs to set up manually
            
            # Try to authenticate silently
            success, message = self.sheets_manager.authenticate(silent=True)
            if not success:
                return  # Authentication failed, user needs to set up manually
            
            # Check if the spreadsheet is accessible
            if not self.sheets_manager.check_spreadsheet_access():
                return  # Spreadsheet not accessible, user needs to reconnect
            
            # Everything is working, update button states
            self._update_sheets_buttons()
            
        except Exception as e:
            print(f"Auto-check Google Sheets setup failed: {e}")
            # Continue without Google Sheets if auto-check fails

    def _calculate_percentage_change(self, current_usd, previous_usd):
        """Calculate percentage change between two USD values"""
        if previous_usd is None or previous_usd == 0:
            return None
        return ((current_usd - previous_usd) / previous_usd) * 100

    def _update_sheets_buttons(self):
        """Update the state of Google Sheets buttons based on configuration and current calculation"""
        if self.sheets_manager.is_configured():
            if self.sheets_manager.check_spreadsheet_access():
                self.setup_sheets_btn.config(text="Reconfigure Google Sheets")
            else:
                self.setup_sheets_btn.config(text="Reconnect Google Sheets")
            self.open_sheets_btn.config(state="normal")
        else:
            self.setup_sheets_btn.config(text="Setup Google Sheets")
            self.open_sheets_btn.config(state="disabled")

    def on_setup_sheets(self):
        """Setup Google Sheets integration"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.sheets_manager.credentials_file):
                messagebox.showinfo("Setup Required", 
                    "To use Google Sheets, you need to:\n\n"
                    "1. Go to Google Cloud Console (https://console.cloud.google.com)\n"
                    "2. Create a new project or select existing one\n"
                    "3. Enable Google Sheets API\n"
                    "4. Create credentials (OAuth 2.0 Client ID)\n"
                    "5. Download the credentials.json file\n"
                    "6. Place it in the same folder as this application\n\n"
                    "Would you like to open the Google Cloud Console?")
                
                if messagebox.askyesno("Open Console", "Open Google Cloud Console?"):
                    import webbrowser
                    webbrowser.open("https://console.cloud.google.com")
                return
            
            # Authenticate
            success, message = self.sheets_manager.authenticate()
            if not success:
                messagebox.showerror("Authentication Failed", message)
                return
            
            # Create spreadsheet or use existing one
            success, message = self.sheets_manager.create_spreadsheet()
            if success:
                if "existing spreadsheet" in message.lower():
                    messagebox.showinfo("Success", f"Google Sheets connected!\n{message}")
                else:
                    messagebox.showinfo("Success", f"Google Sheets setup complete!\n{message}")
                self._update_sheets_buttons()
            else:
                messagebox.showerror("Setup Failed", message)
                
        except Exception as e:
            messagebox.showerror("Setup Error", f"An error occurred during setup: {e}")

    def on_open_sheets(self):
        """Open the Google Sheets in browser"""
        url = self.sheets_manager.get_spreadsheet_url()
        if url:
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open browser: {e}")
        else:
            messagebox.showwarning("No Spreadsheet", "No spreadsheet configured.")

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