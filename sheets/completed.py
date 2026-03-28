from sheets.client import completed_sheet
from datetime import datetime

def add_completed(data):
    brutto = round(float(data.get("netto", 0)) * 1.23, 2)

    row = [
        data.get("id", ""),  # 🔥 НЕ УПАДЁТ
        data.get("car_number", "").upper(),
        data.get("datetime", ""),
        float(data.get("netto", 0)),
        brutto,
        data.get("comment", ""),
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
            row_date = datetime.strptime(r["datetime"].split(" ")[0], "%d.%m.%Y")
            if row_date >= date_from:
                result.append(r)
        except:
            continue

    return result


def get_my_completed_since(user_display, date_from_str):
    rows = completed_sheet.get_all_records()
    date_from = datetime.strptime(date_from_str, "%d.%m.%Y")

    result = []

    for r in rows:
        if r.get("completed_by") != user_display:
            continue

        try:
            row_date = datetime.strptime(r["datetime"].split(" ")[0], "%d.%m.%Y")
            if row_date >= date_from:
                result.append(r)
        except:
            continue

    return result
