import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")

# 🔥 универсальный путь
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE") or "credentials.json"

# если bothost
if not os.path.exists(CREDENTIALS_FILE):
    CREDENTIALS_FILE = "/app/credentials.json"
