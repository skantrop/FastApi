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


from fastapi import APIRouter, UploadFile, File, Form
# с помощью библиотеки shutil можно сохранять файлы
import shutil


# класс APIRouter похож на класс FastAPI но он предназначен для построения route
video_router = APIRouter()


# едача формы и ее валидация (передали title description с изображением
# и валидировали данные)
@video_router.post("/")
async def upload_video(title: str = Form(...), description: str = Form(...), file: UploadFile = File(...)):
    # перезаписываем загружаемый файл для его сохранения
    info = UploadVideo(title=title, description=description)
    with open(f"{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_name": file.filename, "info": info}


from typing import List


@video_router.post("/image", status_code=201)
async def upload_image(files: List[UploadFile] = File(...)):
    for image in files:
        with open(f"{image.filename}", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    return {"hello": "world!"}


from schema import UploadVideo


@video_router.post("/info/")
async def info_set(info: UploadVideo):
    return info


@video_router.get("/info/")
async def info_get():
    return {"info": "name", "int": 3}


@video_router.get("/get/info/")
async def get_info():
    title = 'Test'
    desc = 'Description'
    return UploadVideo(title=title, description=desc)


from schema import GetVideo, Message
from fastapi.responses import JSONResponse


@video_router.get("/video", response_model=GetVideo, responses={404: {"model": Message}})
async def get_video():
    user = {"id": 25, "name": "Mike"}
    video = {"title": "Test", "description": "Description"}
    info = GetVideo(user=user, video=video)
    # return GetVideo(user=user, video=video)
    return JSONResponse(status_code=200, content={"message": info.dict()})

from fastapi import Request
@video_router.get("/test")
async def get_test(req: Request):
    print(req.base_url)
    return {}
