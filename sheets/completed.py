from sheets.client import completed_sheet
from datetime import datetime

def add_completed(data):
    brutto = round(float(data["netto"]) * 1.23, 2)

    row = [
        data["id"],
        data["car_number"].upper(),
        data["datetime"],
        float(data["netto"]),
        brutto,
        data["comment"],
        data.get("created_by", ""),
        data.get("completed_by", "")
    ]

    completed_sheet.append_row(row)

# 🔥 ДЛЯ БУХГАЛТЕРА (ВОЗВРАЩАЕМ)
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

# 🔥 ДЛЯ МЕХАНИКА
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
