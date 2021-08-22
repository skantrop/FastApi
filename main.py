# #1. импортируем из fastapi класс FastAPI
# from fastapi import FastAPI
#
# #создаем объект FastAPI
# app = FastAPI()
#
#
# # строим функции(эндпоинты) основываясь на объекте
# # (декоратор на имя нашего объекта, метод HTTP, (указываем адрес(url))
# @app.get("/")
# async def root():
#     return {"message": "hi"}
#


from fastapi import FastAPI, UploadFile, File
# с помощью библиотеки shutil можно сохранять файлы
import shutil


app = FastAPI()

@app.post("/")
async def upload_video(file: UploadFile = File(...)):
    #перезаписываем загружаемый файл для его сохранения
    with open(f"{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_name": file.filename}

from typing import List

@app.post("/image")
async def upload_image(files: List[UploadFile] = File(...)):
    for image in files:
        with open(f"{image.filename}", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    return {"hello": "world!"}
