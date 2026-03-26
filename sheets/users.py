from sheets.client import users_sheet

def get_role(telegram_id: int):
    data = users_sheet.get_all_records()
    for row in data:
        if str(row["telegram_id"]) == str(telegram_id):
            return row["role"]
    return None

def get_users_by_role(role: str):
    data = users_sheet.get_all_records()
    return [row["telegram_id"] for row in data if row["role"] == role]
