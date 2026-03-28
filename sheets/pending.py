from sheets.client import pending_sheet

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
        ""  # assigned_to
    ]
    pending_sheet.append_row(row)

def get_pending():
    return pending_sheet.get_all_records()

def update_status(service_id, status, assigned_to=None):
    rows = pending_sheet.get_all_values()

    for i, row in enumerate(rows):
        if row[0] == service_id:
            pending_sheet.update_cell(i+1, 6, status)  # status

            if assigned_to:
                pending_sheet.update_cell(i+1, 8, assigned_to)  # assigned_to
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
