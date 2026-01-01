import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =====================================================
# GOOGLE SHEETS LOGGER FOR MIDAS BOT
# =====================================================

def log_trade_to_sheets(trade_data):
    """
    Logs trade details to Google Sheets.
    Requires the Google service account JSON key file shared with the sheet.
    """
    try:
        # Define Google Sheets API scope
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # Load credentials (ensure your JSON key file is in the same directory)
        creds = ServiceAccountCredentials.from_json_keyfile_name("midas_service_account.json", scope)
        client = gspread.authorize(creds)

        # Open your Google Sheet (edit name to match your sheet)
        sheet = client.open("MidasBotSheetLogger").sheet1

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
