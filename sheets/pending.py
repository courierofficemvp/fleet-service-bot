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
        data.get("created_by", "")
    ]
    pending_sheet.append_row(row)

def get_pending():
    return pending_sheet.get_all_records()

def delete_pending(service_id):
    rows = pending_sheet.get_all_values()
    for i, row in enumerate(rows):
        if row[0] == service_id:
            pending_sheet.delete_rows(i + 1)
            return

def get_by_id(service_id):
    rows = pending_sheet.get_all_records()
    for r in rows:
        if str(r.get("id", "")) == str(service_id):
            return r
    return None
