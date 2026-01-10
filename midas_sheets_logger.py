import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

# =====================================================
# GOOGLE SHEETS LOGGER FOR MIDAS BOT
# =====================================================

def log_trade_to_sheets(trade_data):
    """
    Logs trade details to Google Sheets.
    Loads Google credentials from the Render environment variable
    GOOGLE_APPLICATION_CREDENTIALS_JSON (not from a file).
    """

    try:
        # Define Google Sheets API scope
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # Load credentials from environment (Render)
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not creds_json:
            raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON in environment variables")

        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Open your Google Sheet (edit name to match your sheet)
        sheet_name = os.getenv("GOOGLE_SHEET_NAME", "MIDAS_Trade_Log")
        sheet = client.open(sheet_name).sheet1

        # Add timestamp if not included
        if "time" not in trade_data:
            trade_data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Convert dict values to a list (ensures order)
        row = [trade_data.get(k, "") for k in ["time", "pair", "signal", "entry", "exit", "profit", "balance"]]

        # Append to the sheet
        sheet.append_row(row)
        print(f"✅ Trade logged to Google Sheets: {trade_data}")

    except Exception as e:
        print(f"⚠️ Could not log to Google Sheets: {e}")