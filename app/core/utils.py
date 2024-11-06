def store_log(text: str, title: str = None):
    with open("log.txt", "a+", encoding="utf-8") as file:
        if title is not None:
            file.write(title.center(30, "-") + "\n")

        file.write(text + "\n\n")
