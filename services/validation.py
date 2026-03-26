from datetime import datetime

def validate_datetime(text):
    try:
        datetime.strptime(text, "%d.%m.%Y %H:%M")
        return True
    except:
        return False

def normalize_car(car):
    return car.upper()
