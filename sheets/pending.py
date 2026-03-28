from sheets.client import pending_sheet
from datetime import datetime

def normalize_car(car):
    return str(car).strip().upper()

def add_pending(data):
    row = [
        data["id"],
        normalize_car(data["car_number"]),
        data["datetime"],
        data["work_description"],
        data["driver_phone"],
        "pending",
        data.get("created_by", ""),
        ""
    ]
    pending_sheet.append_row(row)

def get_pending():
    return pending_sheet.get_all_records()

def get_my_services_since(user_display, date_from_str):
    rows = pending_sheet.get_all_records()
    date_from = datetime.strptime(date_from_str, "%d.%m.%Y")

    result = []
    for r in rows:
        if r.get("assigned_to") != user_display:
            continue

        try:
            row_date = datetime.strptime(r["datetime"].split(" ")[0], "%d.%m.%Y")
            if row_date >= date_from:
                result.append(r)
        except:
            continue

    return result

def update_status(service_id, status, assigned_to=None):
    rows = pending_sheet.get_all_values()

    for i, row in enumerate(rows):
        if row[0] == service_id:
            pending_sheet.update_cell(i+1, 6, status)

            if assigned_to:
                pending_sheet.update_cell(i+1, 8, assigned_to)
            return True
    return False

def get_by_id(service_id):
    rows = pending_sheet.get_all_records()
    for r in rows:
        if r["id"] == service_id:
            return r
    return None

def delete_pending(service_id):
    rows = pending_sheet.get_all_values()
    for i, row in enumerate(rows):
        if row[0] == service_id:
            pending_sheet.delete_rows(i+1)
            return
