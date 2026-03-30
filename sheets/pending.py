from uuid import uuid4

from sheets.client import pending_sheet


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


def add_pending(data):
    service_id = str(data.get("id") or uuid4()).strip()

    row = [
        service_id,
        normalize_car(data["car_number"]),
        str(data["datetime"]).strip(),
        str(data["work_description"]).strip(),
        str(data["driver_phone"]).strip(),
        "pending",
        str(data.get("created_by", "")).strip(),
        "",
    ]
    pending_sheet.append_row(row)
    return service_id


def get_pending():
    rows = pending_sheet.get_all_records()
    return [_normalize_row(r) for r in rows]


def get_by_id(service_id):
    service_id = str(service_id).strip()

    for row in get_pending():
        if row["id"] == service_id:
            return row

    return None


def update_status(service_id, status, user=None):
    service_id = str(service_id).strip()
    rows = pending_sheet.get_all_values()

    for i, row in enumerate(rows):
        if not row:
            continue

        if row[0] == service_id:
            updated_row = row[:]

            while len(updated_row) < 8:
                updated_row.append("")

            updated_row[5] = str(status).strip()

            if user is not None:
                updated_row[7] = str(user).strip()

            pending_sheet.update(f"A{i+1}:H{i+1}", [updated_row])
            return True

    return False


def assign_if_free(service_id, user):
    service_id = str(service_id).strip()
    user = str(user).strip()

    service = get_by_id(service_id)
    if not service:
        return False

    if service["status"] != "pending":
        return False

    if service["assigned_to"]:
        return False

    saved = update_status(service_id, "in_progress", user)
    if not saved:
        return False

    updated = get_by_id(service_id)
    if not updated:
        return False

    return (
        updated["status"] == "in_progress"
        and updated["assigned_to"] == user
    )


def delete_pending(service_id):
    service_id = str(service_id).strip()
    rows = pending_sheet.get_all_values()

    for i, row in enumerate(rows):
        if row and row[0] == service_id:
            pending_sheet.delete_rows(i + 1)
            return True

    return False
