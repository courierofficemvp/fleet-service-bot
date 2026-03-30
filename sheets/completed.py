from sheets.client import completed_sheet


def get_completed():
    return completed_sheet.get_all_records()


def exists_completed(service_id: str) -> bool:
    for row in get_completed():
        if str(row.get("id")) == str(service_id):
            return True
    return False


def add_completed(data):
    if exists_completed(data["id"]):
        return False

    row = [
        data.get("id"),
        data.get("car_number"),
        data.get("datetime"),
        data.get("netto"),
        data.get("brutto", ""),
        data.get("comment"),
        data.get("created_by"),
        data.get("completed_by"),
    ]

    completed_sheet.append_row(row)
    return True


def get_my_completed_since(user_id: str, date_from: str):
    from datetime import datetime

    try:
        date_from = datetime.strptime(date_from, "%d.%m.%Y")
    except:
        return []

    result = []

    for row in get_completed():
        if str(row.get("completed_by")) != str(user_id):
            continue

        try:
            row_date = datetime.strptime(row.get("datetime"), "%d.%m.%Y %H:%M")
        except:
            continue

        if row_date >= date_from:
            result.append(row)

    return result

# ===============================
# 🔁 BACKWARD COMPATIBILITY
# ===============================

def get_completed_since(date_from: str):
    from datetime import datetime

    try:
        date_from = datetime.strptime(date_from, "%d.%m.%Y")
    except:
        return []

    result = []

    for row in get_completed():
        try:
            row_date = datetime.strptime(row.get("datetime"), "%d.%m.%Y %H:%M")
        except:
            continue

        if row_date >= date_from:
            result.append(row)

    return result
