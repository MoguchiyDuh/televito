from datetime import datetime
import traceback
from colorama import Fore
import requests
import json

from .core.config import MODEL
from .core.utils import store_log

url = "http://localhost:11434/api/chat"
MODEL_INSTRUCTION = f"""
Parse the following rental property listing text into structured data. All value must be the same type as provided. The language must remain russian. Post date is {datetime.now()}
YOU MUST ONLY RETURN A JSON OBJECT WITH THESE FIELDS, NO COMMENTS NEEDED:
- location: str - Extract the location after the phrase "Локация -".
- status: datetime - If the phrase "свободна сейчас" is present, return the post date. If there’s a phrase "свободна с" followed by a date in Russian (e.g., "1 мая 2023"), extract the date and return it as "YYYY-MM-DD". If the text contains words indicating a future date, such as "свободна через 2 недели," "свободна через 3 дня," or "свободна завтра," calculate the future date based on the time specified and return it in the format "YYYY-MM-DD". If the text does not contain a future date or reference to a date, return `None`.
- price: float - Extract the numeric price (in euros) from the third line of text. Convert this to a float. If no price is specified, set this to `None`.
- duration: int - Extract the lease duration as an integer, specifically after the phrase "Срок аренды - от X месяцев". If this is missing, set the value as `None`.
- is_new: bool - If the phrase "Новый дом" appears anywhere in the text, set this to `true`. Otherwise, set to `False`.
- rooms: float - The number of rooms, which appears on the line with "комнат". For studio apartments, return `1.0`; if listed as "Другое", return `None`.
- room_description: str - If there’s a description of rooms within parentheses, extract the text inside parentheses without them. If none, set to `None`.
- area: float - Extract the area in square meters (m²) from a line containing "Площадь". Return as a float.
- floor: int - Extract the floor number. There will be the format "X/Y", return only int(X). If it’s a high basement, set floor to `0`.
- floors_in_building: int - Extract the total number of floors in the building. There will be the format "X/Y", return only int(Y).
- pets_allowed: bool - If the phrase "С животными – можно" is present, set to `true`. Otherwise, set to `False`.
- parking: str - Extract any information about parking if it appears after "🚗" and before any hashtags (`#`). If none, set to `None`.
"""


def generate_response(history: list, temperature: float, top_p: float) -> str:
    data = {
        "model": MODEL,
        "messages": history,
        "options": {"temperature": temperature, "top_p": top_p},
    }

    response = requests.post(url, json=data, stream=True)

    all_responses = []
    for line in response.iter_lines():
        if line:
            line_json = json.loads(line.decode("utf-8"))
            all_responses.append(line_json.get("message").get("content"))

    full_response = "".join(all_responses)
    return full_response


def model_parse(
    prompt: str, post_datetime: datetime, temperature: float = 0.7, top_p: float = 0.9
) -> dict:
    HISTORY = [{"role": "user", "content": MODEL_INSTRUCTION}]
    HISTORY.append({"role": "user", "content": prompt})
    response = generate_response(HISTORY, temperature, top_p)
    HISTORY.append({"role": "agent", "content": response})

    while True:
        store_log(response, "MODEL RESPONSE")
        try:
            start = response.find("{")
            end = response.find("}") + 1
            result = json.loads(response[start:end])
            if result["status"] == "available now":
                result["status"] = post_datetime
            elif result["status"] is not None:  # YYYY-MM-DD
                result["status"] = datetime.fromisoformat(result["status"])

            expected_types = {
                "location": str,
                "status": datetime,
                "price": float,
                "duration": int,
                "is_new": bool,
                "rooms": float,
                "room_description": str,
                "area": float,
                "floor": int,
                "floors_in_building": int,
                "pets_allowed": bool,
            }
            for key, expected_type in expected_types.items():
                if (
                    not isinstance(result[key], expected_type)
                    and result[key] is not None
                ):
                    raise TypeError(
                        f"Expected {expected_type} for key '{key}' but got {type(result[key])}"
                    )

            return result
        except Exception as e:
            exception = traceback.format_exc()
            store_log(exception, "MODEL EXCEPTION")
            HISTORY.append(
                {
                    "role": "user",
                    "content": exception
                    + "\n The exception raised while parsing the result. Try parse again with the same prompt. DONT RETURN HOW TO FIX THIS EXCEPTION, PARSE THE TEXT ONCE AGAIN",
                }
            )
            response = generate_response(HISTORY, temperature, top_p)


def start_talking():
    while True:
        print(Fore.BLUE, end="")
        prompt = input(">>> ")

        if prompt.lower() == "exit":
            break
        elif '"""' in prompt:
            while True:
                line = input('">>> ')
                prompt += "\n" + line
                if '"""' in line:
                    break

        print(Fore.RESET, end="")
        response: str = generate_response(prompt)
        print(Fore.YELLOW + response + Fore.RESET)
