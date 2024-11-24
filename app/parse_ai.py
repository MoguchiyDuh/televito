from datetime import datetime
import re
import traceback
from colorama import Fore
import requests
import json

from .core.config import MODEL
from .core.utils import store_log

# Configuration for API URL and model instruction
API_URL = "http://localhost:11434/api/chat"
MODEL_INSTRUCTION = """
You must return the data in JSON FORMAT about apartment rentals according to the format below. Follow these rules STRICTLY!:
- DO NOT ADD NEW FIELDS, YOU ARE ALLOWED TO USE ONLY PROVIDED.
- DO NOT change data types other than those provided.
- The output must be VALID JSON FORMAT!

STRUCTURE:
* location - copy the field about an apartment location
* status - calculate the date from when the apartment will be available in format "YYYY-MM-DD" or paste the post date if the field is "свободна сейчас"
* price - copy the number - price
* duration - copy the number - minimal lease duration
* is_new - set "true" if there is a field "Новый дом", set false otherwise
* rooms - copy the number - total rooms in the apartment
* room_description - copy apartment info - the text that is inside the parentheses after the rooms amout
* area - copy the number - total apartment area
* floor - copy the number - amount of rooms in the apartment. it is the first number in the field before slash '/'. set 'null' if not provided
* floors_in_building - copy the number - total floors in a building. it is the second number in the field after slash '/'.
* pets_allowed - set 'true' if "с животными - можно", set 'false' otherwise
* parking - copy info about parking without the word "Парковка -", if there is one. set 'null' if info isn't provided
* IGNORE OTHER FIELDS THAT AREN'T DISCRIBED HERE!


**Example Input and Expected Output**:

TEXT1:
ДАТА ПОСТА: 01.11.2024
🏡 Локация - Hercegovačka , Belgrade Waterfront, Savski venac
🔹 Актуальность - свободна с 06 дек. 2024
💸 1400 €
🔹 Срок аренды - от 12 месяцев
🔹 Новый дом
🔹 2.0 комнаты 
🔹 Площадь 55 m²
🔹 15/23 этаж
🐾 С животными – нельзя
📞 Запись на просмотр @BelgradeTeam
🚗 Парковка -  на участке

OUTPUT1:
{
"location": "Hercegovačka, Belgrade Waterfront, Savski venac",
"status": "06.12.2024",
"price": 1400.0,
"duration": 12,
"is_new": true, // there is a field "Новый дом"
"rooms": 2.0,
"room_description": null, // there is no information about apartment in parentheses
"area": 55.0,
"floor": 15,
"floors_in_building": 23,
"pets_allowed": false,
"parking": "на участке" // text without "Парковка -" and a sticker
}

TEXT2:
ДАТА ПОСТА: 01.11.2024
🏡 Локация - Vojvode Bogdana , Vukov spomenik, Zvezdara
🔹 Актуальность - свободна сейчас
💸 1200 €
🔹 Срок аренды - от 12 месяцев
🔹 3.0 комнаты (2 спальни)
🔹 Площадь 94 m²
🔹 2/5 этаж
🐾 С животными – нельзя
📞 Запись на просмотр @BelgradeTeam
🚗 Есть cвое машино-место

OUTPUT2:
{
"location": "Vojvode Bogdana, Vukov spomenik, Zvezdara",
"status": "01.11.2024", //because the POST DATE is 01.11.2024 and the status is "свободна сейчас"
"price": 1200.0,
"duration": 12,
"is_new": false, // the is no such field
"rooms": 3.0,
"room_description": "2 спальни", // there is info in parentheses "🔹 3.0 комнаты (2 спальни)"
"area": 94.0,
"floor": 2,
"floors_in_building": 5,
"pets_allowed": false,
"parking": "Есть cвое машино-место"
}

TEXT3:
ДАТА ПОСТА: 01.11.2024
🏡 Локация -  Булевар Арсенија Чарнојевића, Novi Beograd 
🔹 Актуальность - свободна с 24 сентября
💸 900 €
🔹 Срок аренды - от 6 месяцев
🔹 2,0 комнаты
🔹 Площадь 67 m²
🔹 5 этаж
🐾 С животными – нельзя
📞 Запись на просмотр @BelgradeTeam
#цена800_1100

OUTPUT3:
{
"location": "Булевар Арсенија Чарнојевића, Novi Beograd",
"status": "24.09.2024", // current year is 2024, so copy the POST DATE with the current year
"price": 900,
"duration": 6,
"is_new": false, // the is no such field
"rooms": 3.0,
"room_description": null, // there is no information about apartment in parentheses
"area": 67,
"floor": 5,
"floors_in_building": null, // the second number after slash '/' isn't provided, set to 'null'
"pets_allowed": false,
"parking": null // no info about parking, set to 'null'
}

TEXT4:
ДАТА ПОСТА: 01.11.2024
🏡 Локация - Alberta Ajnštajna , Višnjica, Palilula 
🔹 Актуальность - свободна 20 
💸 700 €
🔹 Срок аренды - от 12 месяцев
🔹 Новый дом
🔹 3.0 комнаты (2 спальни)
🔹 Площадь 73 m²
🔹 3/3 этаж
🐾 С животными – нельзя
📞 Запись на просмотр @BelgradeTeam
🚗 Cвободная зона

OUTPUT4:
{
"location": "Alberta Ajnštajna , Višnjica, Palilula",
"status": "20.11.2024" // set the current month (11 in the POST DATE in this case) and the current year (2024 in the POST DATE in this case) if they didn't pass.
"price": 700,
"duration": 12,
"is_new": true,
"rooms": 3.0,
"room_description": "2 спальни",
"area": 73,
"floor": 3,
"floors_in_building": 3,
"pets_allowed": false,
"parking": "Cвободная зона"
}

TEXT5:
ДАТА ПОСТА: 10.10.2024
🏡 Локация - Maršala Birjuzova , Centar, Stari grad 
🔹 Актуальность - свободна 01 
💸 1700 €
🔹 Срок аренды - от 12 месяцев
🔹 3.0 комнаты (3 спальни, 2 ванные)
🔹 Площадь 94 m²
🔹 2/4 этаж
🐾 С животными – нельзя
📞 Запись на просмотр @BelgradeTeam
🚗 Парковка -  Зона А

OUTPUT5:
{
"location": "Maršala Birjuzova , Centar, Stari grad",
"status": "01.11.2024" // set the next month (01.10.2024 is already passed, so set to the next month 01.11.2024) and the current year (2024 in the POST DATE in this case) if they didn't pass.
"price": 1700,
"duration": 12,
"is_new": false,
"rooms": 3.0,
"room_description": "3 спальни, 2 ванные",
"area": 94,
"floor": 2,
"floors_in_building": 4,
"pets_allowed": false,
"parking": "Зона А"
}
"""


def check_response_types(result: dict):
    """Ensures response fields match expected types."""
    expected_types = {
        "location": str,
        "status": datetime,
        "price": (float, int),
        "duration": int,
        "is_new": bool,
        "rooms": (float, int),
        "room_description": str,
        "area": (float, int),
        "floor": int,
        "floors_in_building": int,
        "pets_allowed": bool,
        "parking": str,
    }

    if len(result) != len(expected_types):
        raise ValueError(f"Unexpected response, got {len(result)} fields")

    for key, expected_type in expected_types.items():
        if (
            not isinstance(result.get(key), expected_type)
            and result.get(key) is not None
        ):
            raise TypeError(
                f"Expected {expected_type} for '{key}', got {type(result.get(key))}"
            )


def request_model_response(history: list[dict], temperature=0.7, top_p=0.9):
    """Requests a response from the AI model using specified parameters."""
    data = {
        "model": MODEL,
        "messages": history,
        "options": {"temperature": temperature, "top_p": top_p},
    }
    try:
        response = requests.post(API_URL, json=data, stream=True)
        response.raise_for_status()
        return "".join(
            json.loads(line.decode("utf-8")).get("message", {}).get("content", "")
            for line in response.iter_lines()
            if line
        )
    except requests.RequestException as e:
        store_log(str(e), "API REQUEST ERROR")
        print(f"{Fore.RED}❌ Error communicating with model API:{Fore.RESET}", e)
        return None


def parse_with_ai(
    prompt: str, post_datetime: datetime, temperature: float = 0.7, top_p: float = 0.9
) -> dict:
    """Parses rental listing text via an AI model, with error handling and retries."""
    history = [
        {
            "role": "user",
            "content": MODEL_INSTRUCTION,
        },
        {
            "role": "user",
            "content": f"ДАТА ПОСТА: {post_datetime.strftime('Y%-%m-%d')}\n" + prompt,
        },
    ]
    errors_count, max_errors = 0, 3

    while errors_count < max_errors:
        response = request_model_response(history, temperature, top_p)
        if response is None:
            errors_count += 1
            continue

        store_log(response, "MODEL RESPONSE")
        try:
            # Attempt to parse JSON response content
            result = json.loads(re.search(r"\{.*\}", response, re.DOTALL).group())

            # Set the correct date format in 'status' field
            if isinstance(result.get("status"), str):
                result["status"] = datetime.fromisoformat(result["status"])
            else:
                raise TypeError(
                    f"mismatching types! 'status' must be str in format 'YYYY-MM-DD.' to be parsed"
                )

            # Verify types and return the parsed result
            check_response_types(result)
            return result

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            errors_count += 1
            error_info = traceback.format_exception()
            store_log(error_info, f"ERROR PARSING RESPONSE - Attempt {errors_count}")
            print(f"{Fore.RED}❌ Error parsing response. Retrying...{Fore.RESET}")
            history.append(
                {
                    "role": "user",
                    "content": f"Cannot parse your response due to the error: {str(e)}. try to generate our response again",
                }
            )

    print(f"{Fore.RED}❌ Can't parse the post with AI model.{Fore.RESET}")
    return None  # Return None if parsing fails
