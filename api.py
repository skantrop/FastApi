#мпортируем схемы pythonic
from schema import GetVideo, Message, UploadVideo
# импортируем модели ormar
from models import Video, User
from fastapi import APIRouter, UploadFile, File, Form
# с помощью библиотеки shutil можно сохранять файлы
import shutil

from typing import List


# класс APIRouter похож на класс FastAPI но он предназначен для построения route
video_router = APIRouter()


# едача формы и ее валидация (передали title description с изображением
# и валидировали данные)
@video_router.post("/")
async def upload_video(
        title: str = Form(...), description: str = Form(...), file: UploadFile = File(...)
):
    # перезаписываем загружаемый файл для его сохранения
    info = UploadVideo(title=title, description=description)
    with open(f"{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    user = await User.objects.first()
    return await Video.objects.create(file=file.filename, user=user, **info.dict())


# !!!! создаем запрос используя модели ormar !!!
@video_router.post("/video")
async def create_video(video: Video):
    await video.save()
    return video


@video_router.get("/video/{video_pk}", response_model=GetVideo, responses={404: {"model": Message}})
async def get_video(video_pk: int):
    return await Video.objects.select_related('user').get(pk=video_pk)


from fastapi import Request
@video_router.get("/test")
async def get_test(req: Request):
    print(req.base_url)
    return {}


