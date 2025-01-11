from datetime import date
import re
from core.logger import televito_logger


def parse_date(date_str: str, post_date: date) -> date:
    """Converts Russian date text to a datetime object."""
    date_str = date_str.replace("г", "").replace(".", " ").strip()
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
    date_parts = date_str.split()
    day = int(date_parts[0])

    try:
        month = int(date_parts[1])
    except ValueError:
        month = months_map.get(date_parts[1][:3].lower())
    except IndexError:
        if post_date.day <= day:
            month = post_date.month
        else:
            month = post_date.month + 1

    year = (
        int(date_parts[2])
        if len(date_parts) > 2
        else post_date.year if post_date.month <= month else post_date.year + 1
    )
    return date(year=year, month=month, day=day)


def parse_text(text: str, post_date: date) -> dict | None:
    """Parses rental listing text to structured data."""
    lines = text.strip().split("\n")
    result = {
        "location": None,
        "status": None,
        "price": None,
        "duration": None,
        "is_new": False,
        "rooms": None,
        "room_description": None,
        "area": None,
        "floor": None,
        "floors_in_building": None,
        "pets_allowed": False,
        "parking": None,
    }
    try:
        for line in lines:
            line = line.lower().strip()

            if "локация" in line:
                result["location"] = (
                    re.search(r"локация -(.+)", line)
                    .group(1)
                    .replace(" ,", ",")
                    .strip()
                )
                televito_logger.debug(result["location"])

            elif "актуальность" in line:
                if "свободна сейчас" in line:
                    result["status"] = post_date
                elif "свободна" in line:
                    status_match = re.search(r"\d{1,2}.*", line)
                    result["status"] = parse_date(
                        status_match.group(0),
                        post_date,
                    )
                televito_logger.debug(result["status"])

            elif "новый дом" in line:
                result["is_new"] = True
                televito_logger.debug(result["is_new"])

            elif "💸" in line:
                result["price"] = float(
                    re.search(r"(\d+(\.\d+)?)", line).group(1).replace(",", ".")
                )
                televito_logger.debug(result["price"])

            elif "срок аренды" in line:
                duration_match = re.search(r"от (\d+)", line)
                result["duration"] = int(duration_match.group(1))
                televito_logger.debug(result["duration"])

            elif "комнат" in line or "студия" in line:
                if "студия" in line:
                    result["rooms"] = 1.0
                else:
                    line = line.replace(",", ".").replace("+", "")
                    result["rooms"] = float(
                        re.search(r"(\d+(\.\d+)?)\s+комнат", line)
                        .group(1)
                        .replace(",", ".")
                    )
                televito_logger.debug(result["rooms"])

                room_description_match = re.search(r"\((.+)\)", line)
                if room_description_match:
                    result["room_description"] = room_description_match.group(1)
                    televito_logger.debug(result["room_description"])

            elif "площадь" in line:
                result["area"] = float(re.search(r"площадь (\d+)", line).group(1))
                televito_logger.debug(result["area"])

            elif "этаж" in line:
                if "высокий цокольный этаж" in line:
                    result["floor"] = 0
                elif "подвал" in line:
                    result["floor"] = -1
                else:
                    result["floor"] = int(re.search(r"(\d+)/", line).group(1))
                televito_logger.debug(result["floor"])

                floors_in_building_match = re.search(r"/(\d+)", line)
                if floors_in_building_match:
                    result["floors_in_building"] = int(
                        floors_in_building_match.group(1)
                    )
                    televito_logger.debug(result["floors_in_building"])

            elif "с животными" in line:
                result["pets_allowed"] = "можно" in line
                televito_logger.debug(result["pets_allowed"])

            elif "парковка" in line:
                result["parking"] = (
                    line.replace("🚗", "").replace("парковка -", "").strip()
                )
                televito_logger.debug(result["parking"])

        televito_logger.info(f"Listing {post_date} parsed successfully")
        return result

    except Exception as e:
        televito_logger.error(f"Error parsing post {post_date}: {e}\n{text}")
        return None
