#мпортируем схемы pythonic
from starlette.background import BackgroundTasks
from fastapi.responses import StreamingResponse
from schema import GetVideo, Message, UploadVideo
from fastapi import Request
# импортируем модели ormar
from models import Video, User
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services import write_video


# с помощью библиотеки shutil можно сохранять файлы
import shutil

from typing import List


# класс APIRouter похож на класс FastAPI но он предназначен для построения route
video_router = APIRouter()


# едача формы и ее валидация (передали title description с изображением
# и валидировали данные)
@video_router.post("/")
async def create_video(
        background_tasks: BackgroundTasks,
        title: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...)
):
    # директория куда будут аплоудиться видеофайлы
    file_name = f"media/{file.filename}"
    # проверка формата видео, в случает если это не mp4 забрасывается ошибка
    if file.content_type == "video/mp4":
        # такс который выполняется на заднем фоне приложения
        background_tasks.add_task(write_video, # ф-ция сохраняющая видео
                                  file_name, # путь к директории в которой файл будет сохраняться
                                  file # сохраняемый файл
                                  )
    else:
        raise HTTPException(status_code=418, detail="It isn't mp4")
    # перезаписываем загружаемый файл для его сохранения
    info = UploadVideo(title=title, description=description)
    user = await User.objects.first()
    return await Video.objects.create(file=file_name, user=user, **info.dict())


# !!!! создаем запрос используя модели ormar !!!
# @video_router.post("/video")
# async def create_video(video: Video):
#     await video.save()
#     return video


@video_router.get("/video/{video_pk}/", response_model=GetVideo, responses={404: {"model": Message}})
# асинхронная функция которая кидает запрос в БД по primary_key
async def get_video(video_pk: int):
    # вытаскиваем объект из БД
    file = await Video.objects.select_related('user').get(pk=video_pk)
    # получаем путь к файлу, т.к файлы в формате JSON используем метод dict)
    file_like = open(file.dict().get("file"), mode="rb")
    return StreamingResponse(file_like, media_type='video/mp4')


@video_router.get("/test")
async def get_test(req: Request):
    print(req.base_url)
    return {}


# отдача файла на воспроизведение
# делаем стримнговый поток
async def fake_video_streamer():
    for i in range(10):
        yield b"some fake video bytes"


@video_router.get("/fake")
async def main():
    return StreamingResponse(fake_video_streamer())


