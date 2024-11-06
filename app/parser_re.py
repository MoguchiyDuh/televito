from datetime import datetime
import re
import traceback

from colorama import Fore

from .parse_with_model import model_parse
from .core.utils import store_log


def parse_russian_date(date_str: str) -> datetime:
    months = {
        "янв": 1,
        "фев": 2,
        "мар": 3,
        "апр": 4,
        "мая": 5,
        "июн": 6,
        "июл": 7,
        "авг": 8,
        "сент": 9,
        "окт": 10,
        "нояб": 11,
        "дек": 12,
    }

    date_list = date_str.split()
    if len(date_list) != 3:
        return None

    day, month_str, year = date_list
    month = months.get(month_str.lower().replace(".", "").strip())

    return datetime(int(year.strip()), month, int(day.strip()))


def parse_text(text: str, post_datetime: datetime = datetime.now()) -> dict:
    store_log(text, "Parsing text")
    lines = text.strip().split("\n")
    try:
        location = re.search(r"Локация -(.+)", lines[0]).group(1).strip()  # LOCATION

        if "свободна сейчас" in lines[1]:
            status = post_datetime  # STATUS IF FREE

        elif "свободна с" in lines[1]:
            status = parse_russian_date(
                re.search(r"свободна с (.+)", lines[1]).group(1).strip()
            )  # STATUS IF NOT FREE
        else:
            status = None  # STATUS IF NO MATCH

        for index, line in enumerate(lines):
            if "Новый дом" in line:
                is_new = True  # IS NEW IF MATCH
                lines.pop(index)
                break
            else:
                is_new = False

        price = float(
            re.search(r"(\d+(\.\d+)?)", lines[2]).group(1).replace(",", ".")
        )  # PRICE

        duration_match = re.search(r"Срок аренды - от (\d+)", lines[3])
        if duration_match:
            duration = int(duration_match.group(1))  # DURATION IF MATCH
        else:
            duration = None  # DURATION IF NO MATCH
            lines.insert(3, None)

        if "Студия" in lines[4]:
            rooms = 1.0
        elif "Другое" in lines[4]:
            rooms = None
        else:
            rooms = float(
                re.search(r"(\d+([\.,]\d+)?) комнат", lines[4])
                .group(1)
                .replace(",", ".")
            )  # NUMBER OF ROOMS

        room_description_match = re.search(r"\((.+)\)", lines[4])
        room_description = (
            room_description_match.group(1) if room_description_match else None
        )  # ROOM DESCRIPTION IF MATCH

        area = float(re.search(r"Площадь (\d+) m²", lines[5]).group(1))  # AREA

        floor_match = re.search(r"(\d+)/(\d+)", lines[6])
        if floor_match:
            floor = int(floor_match.group(1))  # FLOOR
            floors_in_building = int(floor_match.group(2))  # FLOORS IN BUILDING
        elif "Высокий цокольный этаж" in lines[6]:
            floor = 0  # FLOOR IF HIGH
            floors_in_building = int(re.search(r"/(\d+)", lines[6]).group(1))
        else:
            floor = None
            floors_in_building = None

        pets_allowed = bool(
            re.search(r"С животными – можно", lines[7])
        )  # IF PETS ALLOWED
        if "С животными" not in lines[7]:
            lines.insert(7, None)

        parking = (
            lines[9].replace("🚗", "").replace("Парковка -", "").strip()
            if len(lines) > 9 and "#" not in lines[9]
            else None
        )  # PARKING

        result = {
            "location": location,
            "status": status,
            "price": price,
            "duration": duration,
            "is_new": is_new,
            "rooms": rooms,
            "room_description": room_description,
            "area": area,
            "floor": floor,
            "floors_in_building": floors_in_building,
            "pets_allowed": pets_allowed,
            "parking": parking,
        }
    except:
        store_log(traceback.format_exc(), "ERROR WHILE PARSING TEXT")
        print(
            f"{Fore.YELLOW}⚠️ COULDN'T PARSE TEXT USING REGEX, TRYING AI MODEL PARSER{Fore.RESET}"
        )
        result = model_parse(text, post_datetime, temperature=0.3)

    result_str = "\n".join([f"{k}: {v}" for k, v in result.items()]) + "\n"
    store_log(result_str, "RESULT")

    return result
