from datetime import datetime


def validate_datetime(text: str) -> bool:
    try:
        datetime.strptime((text or "").strip(), "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False


def validate_date(text: str) -> bool:
    try:
        datetime.strptime((text or "").strip(), "%d.%m.%Y")
        return True
    except ValueError:
        return False


def normalize_car(car: str) -> str:
    return str(car).strip().upper()
