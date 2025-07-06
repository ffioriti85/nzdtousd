# -*- coding: utf-8 -*-
"""
Author: AI Assistant
Last updated: 2025-06-27
Version: 0.1.0
Purpose: Google Sheets integration for NZD Percentage Converter.
         Handles authentication, spreadsheet creation, and data upload.
Dependencies: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
"""

import os
import json
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import tkinter as tk
from tkinter import messagebox

# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsManager:
    """Manages Google Sheets integration for the NZD Percentage Converter"""
    
    def __init__(self, app_directory):
        self.app_directory = app_directory
        self.config_file = os.path.join(app_directory, "sheets_config.json")
        self.credentials_file = os.path.join(app_directory, "credentials.json")
        self.token_file = os.path.join(app_directory, "token.json")
        self.service = None
        self.spreadsheet_id = None
        self.sheet_name = "NZD Calculations"
        
        # Load configuration
        self._load_config()
        
    def _load_config(self):
        """Load Google Sheets configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.spreadsheet_id = config.get('spreadsheet_id', '')
                    self.sheet_name = config.get('sheet_name', 'NZD Calculations')
        except Exception as e:
            print(f"Error loading sheets config: {e}")
    
    def _save_config(self):
        """Save Google Sheets configuration"""
        try:
            config = {
                'spreadsheet_id': self.spreadsheet_id,
                'sheet_name': self.sheet_name,
                'credentials_file': 'credentials.json',
                'token_file': 'token.json'
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving sheets config: {e}")
    
    def authenticate(self, silent=False):
        """Authenticate with Google Sheets API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception:
                pass
        
        # If no valid credentials available, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    return False, "credentials.json file not found. Please download it from Google Cloud Console."
                
                # If silent mode and no valid credentials, return failure
                if silent:
                    return False, "No valid credentials available for silent authentication"
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    return False, f"Authentication failed: {e}"
            
            # Save credentials for next run
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                return False, f"Could not save credentials: {e}"
        
        try:
            self.service = build('sheets', 'v4', credentials=creds)
            return True, "Authentication successful"
        except Exception as e:
            return False, f"Could not build service: {e}"
    
    def create_spreadsheet(self, title="NZD Percentage Calculator"):
        """Create a new Google Spreadsheet or use existing one"""
        if not self.service:
            return False, "Not authenticated"
        
        # Check if we already have a spreadsheet ID
        if self.spreadsheet_id:
            try:
                # Try to access the existing spreadsheet
                spreadsheet = self.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
                return True, f"Using existing spreadsheet: {self.spreadsheet_id}"
            except HttpError:
                # Spreadsheet doesn't exist or we don't have access, create new one
                pass
        
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': self.sheet_name,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 8
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            self.spreadsheet_id = spreadsheet['spreadsheetId']
            
            # Set up headers
            headers = [
                'Timestamp', 'NZD Input', 'Percentage', 'NZD Result', 
                'USD Result', 'USD Rate', 'USD Change %', 'Notes'
            ]
            
            self._update_range(f'{self.sheet_name}!A1:H1', [headers])
            
            # Note: Users can manually apply conditional formatting in Google Sheets
            # Format > Conditional formatting > Color scale for the USD Change % column
            
            # Save the spreadsheet ID
            self._save_config()
            
            return True, f"New spreadsheet created: {spreadsheet['spreadsheetId']}"
            
        except HttpError as e:
            return False, f"Error creating spreadsheet: {e}"
    
    def upload_calculation(self, calculation_data):
        """Upload a calculation to Google Sheets"""
        if not self.service or not self.spreadsheet_id:
            return False, "Not authenticated or no spreadsheet selected"
        
        try:
            # Format the data for upload
            row_data = [
                calculation_data.get('timestamp', ''),
                calculation_data.get('nzd_input', ''),
                calculation_data.get('percentage', ''),
                calculation_data.get('nzd_result', ''),
                calculation_data.get('usd_result', ''),
                calculation_data.get('usd_rate', ''),
                calculation_data.get('usd_change_percent', ''),  # Will be raw float or "N/A"
                calculation_data.get('notes', '')
            ]
            
            # Find the next empty row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:A'
            ).execute()
            
            next_row = len(result.get('values', [])) + 1
            
            # Upload the data
            range_name = f'{self.sheet_name}!A{next_row}:H{next_row}'
            self._update_range(range_name, [row_data])
            
            return True, f"Data uploaded to row {next_row}"
            
        except HttpError as e:
            return False, f"Error uploading data: {e}"
    
    def _update_range(self, range_name, values):
        """Update a range in the spreadsheet"""
        body = {
            'values': values
        }
        
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    

    
    def get_spreadsheet_url(self):
        """Get the URL of the current spreadsheet"""
        if self.spreadsheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return None
    
    def get_last_usd_result(self):
        """Get the USD result from the last entry in the spreadsheet"""
        if not self.service or not self.spreadsheet_id:
            return None
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:H'
            ).execute()
            
            values = result.get('values', [])
            if len(values) > 1:  # More than just headers
                last_row = values[-1]
                if len(last_row) > 4 and last_row[4]:  # Check if USD result exists (column E, index 4)
                    try:
                        return float(last_row[4])
                    except (ValueError, IndexError):
                        return None
            return None
        except Exception:
            return None
    
    def is_configured(self):
        """Check if Google Sheets is properly configured"""
        return (self.service is not None and 
                self.spreadsheet_id is not None and 
                os.path.exists(self.credentials_file))
    
    def check_spreadsheet_access(self):
        """Check if the configured spreadsheet is accessible"""
        if not self.service or not self.spreadsheet_id:
            return False
        
        try:
            self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            return True
        except HttpError:
            return False 