from sheets.client import completed_sheet


# ===============================
# 🔧 UTILS
# ===============================

def _normalize_row(row: dict) -> dict:
    return {
        "id": str(row.get("id", "")).strip(),
        "car_number": str(row.get("car_number", "")).strip(),
        "datetime": str(row.get("datetime", "")).strip(),
        "netto": str(row.get("netto", "")).strip(),
        "brutto": str(row.get("brutto", "")).strip(),
        "comment": str(row.get("comment", "")).strip(),
        "created_by": str(row.get("created_by", "")).strip(),
        "completed_by": str(row.get("completed_by", "")).strip(),
    }


# ===============================
# 📥 READ
# ===============================

def get_completed():
    rows = completed_sheet.get_all_records()
    return [_normalize_row(r) for r in rows]


def exists_completed(service_id: str) -> bool:
    service_id = str(service_id).strip()

    for row in get_completed():
        if row["id"] == service_id:
            return True

    return False


# ===============================
# ➕ CREATE
# ===============================

def add_completed(data: dict):
    service_id = str(data.get("id", "")).strip()

    # 🔥 защита от дублей
    if exists_completed(service_id):
        return False

    row = [
        service_id,
        data.get("car_number", ""),
        data.get("datetime", ""),
        data.get("netto", ""),
        data.get("brutto", ""),  # если нет — ок
        data.get("comment", ""),
        data.get("created_by", ""),
        data.get("completed_by", "")
    ]

    completed_sheet.append_row(row)
    return True


# ===============================
# 📊 ФИЛЬТР ПО МЕХАНИКУ
# ===============================

def get_my_completed_since(user: str, date_from: str):
    from datetime import datetime

    try:
        date_from_obj = datetime.strptime(date_from, "%d.%m.%Y")
    except:
        return []

    results = []

    for row in get_completed():
        if row["completed_by"] != user:
            continue

        try:
            row_date = datetime.strptime(row["datetime"], "%d.%m.%Y %H:%M")
        except:
            continue

        if row_date >= date_from_obj:
            results.append(row)

    return results
