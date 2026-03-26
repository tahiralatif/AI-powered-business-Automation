import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def update_competitor_sheet(competitor_name: str, old_price: str, new_price: str, date: str = None):
    """
    Updates the Google Sheet with competitor pricing changes.
    """
    json_path = os.getenv("GOOGLE_SHEETS_JSON_PATH")
    sheet_name = os.getenv("GOOGLE_SHEET_NAME", "CompetitorTracker")
    
    if not json_path or not os.path.exists(json_path):
        print("⚠️ Google Sheets Service Account JSON not found. Skipping sheet update.")
        return

    if not date:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).sheet1
        
        # Append row: Competitor | Old Price | New Price | Change Date | Alert Sent
        sheet.append_row([competitor_name, old_price, new_price, date, "Yes"])
        print(f"📊 Google Sheet updated for {competitor_name}")
        
    except Exception as e:
        print(f"❌ Google Sheets update error: {e}")
