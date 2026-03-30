from sheets.client import users_sheet


def get_role(user):
    user_id = str(user.id).strip()

    rows = users_sheet.get_all_records()

    for row in rows:
        sheet_id = str(row.get("telegram_id", "")).strip()

        if sheet_id == user_id:
            return str(row.get("role", "")).strip().lower()

    return None
