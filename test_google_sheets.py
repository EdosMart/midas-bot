# ✅ MIDAS Sheets Connection Test
# ---------------------------------------
import gspread
from google.oauth2.service_account import Credentials

# Scope for Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authenticate using Render secret file
creds_dict = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

# Open the target Google Sheet by name
SHEET_NAME = "MIDAS_Trade_Log"
gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1

# Add a test row to verify connection
from datetime import datetime
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

sheet.append_row(["✅ MIDAS Sheets Connection Confirmed", timestamp])

print("✅ Successfully connected to Google Sheets!")
print(f"🕒 Test entry added at {timestamp}")