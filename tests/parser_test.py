from datetime import datetime, timedelta
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.parser_re import parse_text


text1 = """
🏡 Локация - Narodnih heroja , Blok 33, Novi Beograd
 🔹 Актуальность - свободна с  01 дек. 2024
 💸 780 €
 🔹 Срок аренды - от 6 месяцев
 🔹 1,5 комнаты 
 🔹 Площадь 50 m²
 🔹 9/9 этаж
 🐾 С животными – можно
 📞 Запись на просмотр @BelgradeTeam
 🚗 Cвободная зона
#цена500_800
"""


def test_text1():
    parsed_text = parse_text(text1)
    assert parsed_text == {
        "location": "Narodnih heroja , Blok 33, Novi Beograd",
        "status": datetime(year=2024, month=12, day=1),
        "price": 780.0,
        "duration": 6,
        "is_new": False,
        "rooms": 1.5,
        "room_description": None,
        "area": 50.0,
        "floor": 9,
        "floors_in_building": 9,
        "pets_allowed": True,
        "parking": "Cвободная зона",
    }


text2 = """
🏡 Локация - Hercegovačka , Belgrade Waterfront, Savski venac
 🔹 Актуальность - свободна с  06 дек. 2024
 💸 1400 €
 🔹 Срок аренды - от 12 месяцев
 🔹 Новый дом
 🔹 2.0 комнаты 
 🔹 Площадь 55 m²
 🔹 15/23 этаж
 🐾 С животными – нельзя
 📞 Запись на просмотр @BelgradeTeam
 🚗 Есть cвое машино-место
#цена1100_1500
"""


def test_text2():
    parsed_text = parse_text(text2)
    assert parsed_text == {
        "location": "Hercegovačka , Belgrade Waterfront, Savski venac",
        "status": datetime(year=2024, month=12, day=6),
        "price": 1400.0,
        "duration": 12,
        "is_new": True,
        "rooms": 2.0,
        "room_description": None,
        "area": 55.0,
        "floor": 15,
        "floors_in_building": 23,
        "pets_allowed": False,
        "parking": "Есть cвое машино-место",
    }


text3 = """
🏡 Локация - Kapetan Mišina , Centar, Stari grad
 🔹 Актуальность - свободна сейчас
 💸 1200 €
 🔹 Срок аренды - от 12 месяцев
 🔹 3.0 комнаты (2 спальни)
 🔹 Площадь 60 m²
 🔹 Высокий цокольный этаж/4 этаж
 🐾 С животными – нельзя
 📞 Запись на просмотр @BelgradeTeam
 🚗 Парковка -  Зона II 
#цена1100_1500
"""


def test_text3():
    current_date = datetime.now()
    parsed_text = parse_text(text3, current_date)
    assert parsed_text == {
        "location": "Kapetan Mišina , Centar, Stari grad",
        "status": current_date,
        "price": 1200.0,
        "duration": 12,
        "is_new": False,
        "rooms": 3.0,
        "room_description": "2 спальни",
        "area": 60.0,
        "floor": 0,
        "floors_in_building": 4,
        "pets_allowed": False,
        "parking": "Зона II",
    }


text4 = """
🏡 Локация - Vojvode Bogdana , Vukov spomenik, Zvezdara
 🔹 Актуальность - свободна с  05 нояб. 2024
 💸 1200 €
 🔹 Срок аренды - от 12 месяцев
 🔹 3.0 комнаты (2 спальни)
 🔹 Площадь 94 m²
 🔹 2/5 этаж
 🐾 С животными – нельзя
 📞 Запись на просмотр @BelgradeTeam
 🚗 Есть cвое машино-место
#цена1100_1500
"""


def test_text4():
    parsed_text = parse_text(text4)
    assert parsed_text == {
        "location": "Vojvode Bogdana , Vukov spomenik, Zvezdara",
        "status": datetime(year=2024, month=11, day=5),
        "price": 1200.0,
        "duration": 12,
        "is_new": False,
        "rooms": 3.0,
        "room_description": "2 спальни",
        "area": 94.0,
        "floor": 2,
        "floors_in_building": 5,
        "pets_allowed": False,
        "parking": "Есть cвое машино-место",
    }


text_for_model = """
🏡 Локация - Južni bulevar , Južni bulevar, Vračar
 🔹 Актуальность - будет свободна завтра
 💸 1000 €
 🔹 Срок аренды - от 12 месяцев
 🔹 5- комнат(3 спальни)
 🔹 Площадь 101 m²
 🔹 8/8 этаж
 🐾 С животными – можно
 📞 Запись на просмотр @BelgradeTeam
 🚗 Парковка -  Бесплатная парковка у здания  Зона III 
#цена800_1100
"""


def test_text_for_model():
    current_datetime = datetime.now()
    parsed_text = parse_text(text_for_model, current_datetime)
    assert parsed_text["status"].day == current_datetime.day + 1

    del parsed_text["status"]

    assert parsed_text == {
        "location": "Južni bulevar , Južni bulevar, Vračar",
        "price": 1000.0,
        "duration": 12,
        "is_new": False,
        "rooms": 5,
        "room_description": "3 спальни",
        "area": 101.0,
        "floor": 8,
        "floors_in_building": 8,
        "pets_allowed": True,
        "parking": "Бесплатная парковка у здания  Зона III",
    }


# test_text_for_model()
