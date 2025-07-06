# Google Sheets Setup Guide

This guide will help you set up Google Sheets integration for the NZD Percentage Converter.

## Prerequisites

1. A Google account
2. Internet connection
3. Python with the required dependencies installed

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter a project name (e.g., "NZD Calculator")
5. Click "Create"

### 2. Enable Google Sheets API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on "Google Sheets API"
4. Click "Enable"

### 3. Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: "NZD Percentage Converter"
   - User support email: Your email
   - Developer contact information: Your email
4. Click "Save and Continue" through the remaining steps
5. For OAuth client ID:
   - Application type: Desktop application
   - Name: "NZD Calculator Desktop"
6. Click "Create"

### 4. Download Credentials

1. After creating the OAuth client ID, click "Download JSON"
2. Rename the downloaded file to `credentials.json`
3. Place `credentials.json` in the same folder as your `main.py` file

### 5. Install Dependencies

Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

### 6. First Run Setup

1. Run the application: `python main.py`
2. Click "Setup Google Sheets"
3. A browser window will open asking you to authorize the application
4. Sign in with your Google account and grant permissions
5. The application will create a new Google Spreadsheet automatically

## How It Works

- **Setup Google Sheets**: Initializes the connection and creates a new spreadsheet
- **Upload to Google Sheets**: Saves the current calculation to the spreadsheet
- **Open Google Sheets**: Opens the spreadsheet in your default browser

## Data Structure

The Google Sheet will have the following columns:
- Timestamp: When the calculation was made
- NZD Input: The original NZD amount
- Percentage: The percentage used
- NZD Result: The calculated NZD result
- USD Result: The converted USD amount
- USD Rate: The exchange rate used
- USD Change %: Percentage change from previous entry (raw float values, e.g., 2.50, -1.75)
- Notes: Additional notes (currently empty)

## Optional: Add Visual Formatting

To make the percentage changes more visually appealing, you can add conditional formatting:

1. Select the entire "USD Change %" column (column G)
2. Go to Format > Conditional formatting
3. Choose "Color scale" 
4. Set:
   - Minimum: Red (for negative values like -1.75)
   - Midpoint: White (for zero)
   - Maximum: Green (for positive values like 2.50)
5. Click "Done"

This will automatically color-code your percentage changes:
- 🟢 Green for increases (positive values)
- 🔴 Red for decreases (negative values)
- ⚪ White for no change (zero)

## Additional Formatting Tips

You can also format the "USD Change %" column to show percentage signs:
1. Select the entire "USD Change %" column
2. Go to Format > Number > Percent
3. Choose the number of decimal places (e.g., 2 decimal places)

This will display values like "2.50%" and "-1.75%" while keeping the underlying numerical values for calculations.

## Troubleshooting

### "credentials.json file not found"
- Make sure you downloaded the credentials file from Google Cloud Console
- Ensure it's named exactly `credentials.json`
- Place it in the same folder as `main.py`

### "Authentication failed"
- Check your internet connection
- Ensure the Google Sheets API is enabled in your project
- Try deleting `token.json` and re-authenticating

### "Error creating spreadsheet"
- Check that you have permission to create spreadsheets in your Google account
- Ensure you're signed into the correct Google account

## Security Notes

- The `credentials.json` file contains sensitive information - keep it secure
- The `token.json` file stores your authentication token - don't share it
- The application only requests permission to access and modify spreadsheets

## Support

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Verify your Google Cloud project setup
3. Ensure you have a stable internet connection
4. Try re-authenticating by deleting `token.json` and running setup again 