from sheets.client import flota_sheet

def normalize_car(car):
    return str(car).strip().upper()

def car_exists(car_number: str):
    car_number = normalize_car(car_number)

    data = flota_sheet.get_all_records()

    for row in data:
        if normalize_car(row["nr rejestracyjny"]) == car_number:
            return True

    return False
