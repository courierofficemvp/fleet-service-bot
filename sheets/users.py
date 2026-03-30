from sheets.client import users_sheet


def get_role(user):
    user_id = str(user.id).strip()

    rows = users_sheet.get_all_records()

    for row in rows:
        sheet_id = str(row.get("telegram_id", "")).strip()

        if sheet_id == user_id:
            return str(row.get("role", "")).strip().lower()

    return None


# ===============================
# 👤 DISPLAY NAME
# ===============================

def get_user_display(user):
    if user.username:
        return f"@{user.username}"
    return user.full_name


# ===============================
# 👥 USERS BY ROLE
# ===============================

def get_users_by_role(role: str):
    role = str(role).strip().lower()

    rows = users_sheet.get_all_records()

    result = []

    for row in rows:
        if str(row.get("role", "")).strip().lower() == role:
            result.append(row)

    return result
