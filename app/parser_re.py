from datetime import date
import re
import traceback
from colorama import Fore

from .parse_ai import parse_with_ai
from .core.utils import store_log


def parse_russian_date(date_str: str, post_date: date) -> date:
    """Converts Russian date text to a datetime object."""
    months_map = {
        "янв": 1,
        "фев": 2,
        "мар": 3,
        "апр": 4,
        "мая": 5,
        "июн": 6,
        "июл": 7,
        "авг": 8,
        "сен": 9,
        "окт": 10,
        "ноя": 11,
        "дек": 12,
    }
    date_parts = date_str.replace(".", "").split()
    day = int(date_parts[0])
    month = (
        months_map.get(date_parts[1][:3].lower())
        if len(date_parts) > 1
        else post_date.month if post_date.day <= day else post_date.month + 1
    )
    year = (
        int(date_parts[2])
        if len(date_parts) > 2
        else post_date.year if post_date.month <= month else post_date.year + 1
    )
    return date(year=year, month=month, day=day)


def parse_text(text: str, post_date: date) -> dict:
    """Parses rental listing text to structured data."""
    store_log(
        "POST DATE: " + post_date.strftime("%Y-%m-%d") + "\n" + text, "TEXT TO PARSE"
    )
    lines = text.strip().split("\n")
    try:
        # Location
        location = (
            re.search(r"Локация -(.+)", lines[0]).group(1).replace(" ,", ",").strip()
        )
        if "Локация" in lines[0]:
            lines.pop(0)

        # Status
        lines[0] = lines[0].lower().strip()
        if "свободна сейчас" in lines[0]:
            status = post_date
        elif "свободна" in lines[0]:
            status_match = re.search(r"(\d{1,2}.*[^ г\.])", lines[0])
            status = parse_russian_date(
                status_match.group(1),
                post_date,
            )
        else:
            None

        if "актуальность" in lines[0]:
            lines.pop(0)

        # Is Building New?
        for index, line in enumerate(lines):
            if "Новый дом" in line:
                is_new = True
                lines.pop(index)
                break
            else:
                is_new = False

        # Price
        price = float(re.search(r"(\d+(\.\d+)?)", lines[0]).group(1).replace(",", "."))
        if "💸" in lines[0]:
            lines.pop(0)

        # Lease Duration
        if "Срок аренды" in lines[0]:
            duration_match = re.search(r"от (\d+)", lines[0])
            duration = int(duration_match.group(1))
        else:
            duration = None

        if "Срок аренды" in lines[0]:
            lines.pop(0)

        # Rooms Count
        rooms_match = re.search(r"(\d+([\.,]\d+)?) комнат", lines[0])
        if "Студия" in lines[0]:
            rooms = 1.0
        elif rooms_match:
            rooms = float(rooms_match.group(1).replace(",", "."))
        else:
            rooms = None

        # Room description
        room_description_match = re.search(r"\((.+)\)", lines[0])
        room_description = (
            room_description_match.group(1) if room_description_match else None
        )
        lines.pop(0)

        # Area
        area = float(re.search(r"Площадь (\d+) m", lines[0]).group(1))
        lines.pop(0)

        # Floor Info
        floor_match = re.search(r"(\d+)/", lines[0])

        if "Высокий цокольный этаж" in lines[0]:
            floor = 0
        elif floor_match:
            floor = int(floor_match.group(1))
        else:
            floor = None

        # Total floors in building
        floors_in_building_match = re.search(r"/(\d+)", lines[0])
        if floors_in_building_match:
            floors_in_building = int(floors_in_building_match.group(1))
        else:
            floors_in_building = None

        if "этаж" in lines[0]:
            lines.pop(0)

        # Are pets allowed?
        pets_allowed = bool(re.search(r"С животными – можно", lines[0]))
        lines.pop(0)

        if "📞" in lines[0]:
            lines.pop(0)

        # Parking Info
        if lines and "#" not in lines[0]:
            parking = lines[0].replace("🚗", "").replace("Парковка -", "").strip()
        else:
            parking = None

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
    except Exception as e:
        store_log(traceback.format_exc(), "ERROR WHILE PARSING TEXT")
        print(
            f"{Fore.YELLOW}⚠️ Couldn't parse text using regex. Trying AI model...{Fore.RESET}"
        )
        # try to parse the post using ai model
        result = parse_with_ai(text, post_date, temperature=0.2)

    if result:
        store_log("\n".join([f"{k}: {v}" for k, v in result.items()]), "RESULT")
    else:
        print(f"{Fore.RED}❌ Parsing failed with both regex and AI.{Fore.RESET}")

    return result
