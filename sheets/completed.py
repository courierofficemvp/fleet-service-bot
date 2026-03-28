from sheets.client import completed_sheet
from datetime import datetime
import uuid

def normalize_car(car):
    return str(car).strip().upper()

def add_completed(data):
    netto = float(str(data["netto"]).replace(",", ".").strip())
    brutto = round(netto * 1.23, 2)

    row = [
        str(uuid.uuid4()),
        normalize_car(data["car_number"]),
        data["datetime"],
        netto,
        brutto,
        data["comment"],
        data.get("created_by", ""),
        data.get("completed_by", "")
    ]

    completed_sheet.append_row(row)

def get_completed_since(date_from_str):
    rows = completed_sheet.get_all_records()
    date_from = datetime.strptime(date_from_str, "%d.%m.%Y")

    result = []
    for r in rows:
        try:
            row_date = datetime.strptime(str(r["datetime"]).split(" ")[0], "%d.%m.%Y")
            if row_date >= date_from:
                result.append(r)
        except Exception:
            continue

    return result
