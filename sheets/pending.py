ffrom sheets.client import pending_sheet
from uuid import uuid4


# ===============================
# 🔧 UTILS
# ===============================

def normalize_car(car):
    return str(car).strip().upper()


def _normalize_row(row: dict) -> dict:
    return {
        "id": str(row.get("id", "")).strip(),
        "car_number": str(row.get("car_number", "")).strip(),
        "datetime": str(row.get("datetime", "")).strip(),
        "work_description": str(row.get("work_description", "")).strip(),
        "driver_phone": str(row.get("driver_phone", "")).strip(),
        "status": str(row.get("status", "")).strip(),
        "created_by": str(row.get("created_by", "")).strip(),
        "assigned_to": str(row.get("assigned_to", "")).strip(),
    }


# ===============================
# ➕ CREATE
# ===============================

def add_pending(data):
    row = [
        str(uuid4()),
        normalize_car(data["car_number"]),
        data["datetime"],
        data["work_description"],
        data["driver_phone"],
        "pending",
        data.get("created_by", ""),
        ""
    ]
    pending_sheet.append_row(row)


# ===============================
# 📥 READ
# ===============================

def get_pending():
    rows = pending_sheet.get_all_records()
    return [_normalize_row(r) for r in rows]


def get_by_id(service_id):
    service_id = str(service_id).strip()

    for r in get_pending():
        if r["id"] == service_id:
            return r

    return None


# ===============================
# 🔁 UPDATE
# ===============================

def update_status(service_id, status, user=None):
    rows = pending_sheet.get_all_values()

    for i, row in enumerate(rows):
        if row[0] == service_id:
            # 🔥 ОДИН update вместо двух
            updated_row = row.copy()

            updated_row[5] = status  # status

            if user is not None:
                updated_row[7] = user  # assigned_to

            pending_sheet.update(f"A{i+1}:H{i+1}", [updated_row])
            return True

    return False


# ===============================
# 🔒 SAFE ASSIGN (анти-гонка)
# ===============================

def assign_if_free(service_id, user):
    """
    Максимально безопасное назначение для Google Sheets
    """

    service = get_by_id(service_id)

    if not service:
        return False

    if service["status"] != "pending":
        return False

    if service["assigned_to"]:
        return False

    # обновляем
    update_status(service_id, "in_progress", user)

    # проверяем после записи
    updated = get_by_id(service_id)

    if not updated:
        return False

    return (
        updated["status"] == "in_progress"
        and updated["assigned_to"] == user
    )


# ===============================
# ❌ DELETE
# ===============================

def delete_pending(service_id):
    rows = pending_sheet.get_all_values()

    for i, row in enumerate(rows):
        if row[0] == service_id:
            pending_sheet.delete_rows(i+1)
            return True

    return False
