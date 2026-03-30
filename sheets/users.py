from sheets.client import users_sheet


def get_role(telegram_id):
    telegram_id = str(telegram_id).strip()

    data = users_sheet.get_all_records()

    print("DEBUG USERS:", data)

    for row in data:
        # нормализация ключей
        normalized = {str(k).strip().lower(): v for k, v in row.items()}

        row_id = str(normalized.get("telegram_id", "")).strip()
        role = str(normalized.get("role", "")).strip()

        print(f"CHECK ROW: {row_id} == {telegram_id}")

        if row_id == telegram_id:
            return role

    return None


def get_users_by_role(role: str):
    data = users_sheet.get_all_records()
    result = []

    for row in data:
        normalized = {str(k).strip().lower(): v for k, v in row.items()}

        if normalized.get("role") == role:
            result.append(normalized.get("telegram_id"))

    return result


def get_user_display(user):
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not full_name:
        full_name = user.username or str(user.id)

    role = get_role(user.id) or "unknown"
    return f"{full_name} | {role}"
