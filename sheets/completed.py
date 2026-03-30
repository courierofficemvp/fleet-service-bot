from datetime import datetime

from sheets.client import completed_sheet


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


def get_completed():
    rows = completed_sheet.get_all_records()
    return [_normalize_row(r) for r in rows]


def exists_completed(service_id: str) -> bool:
    service_id = str(service_id).strip()

    for row in get_completed():
        if row["id"] == service_id:
            return True

    return False


def _to_float(value):
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value or "").replace(",", ".").replace("zł", "").strip()
    return float(text)


def add_completed(data: dict):
    service_id = str(data.get("id", "")).strip()

    if not service_id:
        return False

    if exists_completed(service_id):
        return False

    try:
        netto = round(_to_float(data.get("netto", 0)), 2)
    except Exception:
        return False

    brutto_raw = data.get("brutto", "")
    try:
        brutto = round(_to_float(brutto_raw), 2) if str(brutto_raw).strip() else round(netto * 1.23, 2)
    except Exception:
        brutto = round(netto * 1.23, 2)

    row = [
        service_id,
        str(data.get("car_number", "")).strip(),
        str(data.get("datetime", "")).strip(),
        netto,
        brutto,
        str(data.get("comment", "")).strip(),
        str(data.get("created_by", "")).strip(),
        str(data.get("completed_by", "")).strip(),
    ]

    completed_sheet.append_row(row)
    return True


def get_completed_since(date_from_str):
    date_from = datetime.strptime(str(date_from_str).strip(), "%d.%m.%Y")
    result = []

    for row in get_completed():
        try:
            row_date = datetime.strptime(row["datetime"], "%d.%m.%Y %H:%M")
        except Exception:
            try:
                row_date = datetime.strptime(row["datetime"].split(" ")[0], "%d.%m.%Y")
            except Exception:
                continue

        if row_date >= date_from:
            result.append(row)

    return result


def get_my_completed_since(user: str, date_from: str):
    date_from_obj = datetime.strptime(str(date_from).strip(), "%d.%m.%Y")
    results = []

    for row in get_completed():
        if row["completed_by"] != str(user).strip():
            continue

        try:
            row_date = datetime.strptime(row["datetime"], "%d.%m.%Y %H:%M")
        except Exception:
            try:
                row_date = datetime.strptime(row["datetime"].split(" ")[0], "%d.%m.%Y")
            except Exception:
                continue

        if row_date >= date_from_obj:
            results.append(row)

    return results
