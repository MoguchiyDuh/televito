import os
import shutil
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status


def store_log(text: str, title: str = None):
    with open("log.txt", "a+", encoding="utf-8") as file:
        if title is not None:
            file.write(title.center(30, "-") + "\n")

        file.write(text + "\n\n")


def save_image(image: UploadFile, dir: str) -> str:
    file_extension = image.filename.split(".")[-1]
    if file_extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image format"
        )
    file_name = f"{uuid4()}.{file_extension}"
    file_path = os.path.join(dir, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return file_path
