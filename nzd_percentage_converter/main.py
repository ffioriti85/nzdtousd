# -*- coding: utf-8 -*-
"""
Author: AI Assistant
Last updated: 2025-06-27
Version: 0.1.0 (Stable Release)
Purpose: Main application file for NZD Percentage Converter GUI tool.
         Features: NZD percentage calculation, live USD conversion, 
         percentage persistence, and error handling.
Dependencies: tkinter (standard), json (standard), requests (external)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
access_key = "da30bcd9f07ffd758fe1d367c87f036a"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

class NZDPercentageConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NZD Percentage Converter")
        self.geometry("400x250")
        self.resizable(False, False)
        self.configure(bg="#f9f9f9")
        self._build_ui()
        self._load_last_percentage()

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
            return
        # Save last-used percentage
        self._save_last_percentage(percent_value)
        # Calculate percentage
        nzd_result = nzd_value * (percent_value / 100)
        self.nzd_result_label.config(text=f"NZD Result: {nzd_result:.2f}")
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
        except Exception as e:
            self.usd_result_label.config(text="USD Result: Error")
            messagebox.showerror("API Error", f"Could not fetch USD rate.\n{e}")

if __name__ == "__main__":
    app = NZDPercentageConverterApp()
    app.mainloop() 