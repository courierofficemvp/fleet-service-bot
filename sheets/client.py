import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import CREDENTIALS_FILE, SHEET_ID

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID)

users_sheet = sheet.worksheet("Users")
pending_sheet = sheet.worksheet("Pending_Services")
completed_sheet = sheet.worksheet("Completed_Services")
flota_sheet = sheet.worksheet("Flota")  # 🔥 НОВЫЙ ЛИСТ
