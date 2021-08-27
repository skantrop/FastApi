#мпортируем схемы pythonic
from starlette.background import BackgroundTasks
from fastapi.responses import StreamingResponse
from schema import GetVideo, Message, UploadVideo
from fastapi import Request
# импортируем модели ormar
from models import Video, User
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services import save_video
from starlette.templating import Jinja2Templates
from starlette.responses import StreamingResponse, HTMLResponse



from typing import List


# # подключение шабонов и указывание директории
templates = Jinja2Templates(directory="templates")

# класс APIRouter похож на класс FastAPI но он предназначен для построения route
video_router = APIRouter()


# едача формы и ее валидация (передали title description с изображением
# и валидировали данные)
@video_router.post("/")
async def create_video(
        back_tasks: BackgroundTasks,
        title: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...)
):
    # директория куда будут аплоудиться видеофайлы
    user = await User.objects.first()
    return await save_video(user, file, title, description, back_tasks)


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


# воспроизведение видео
@video_router.get("/index/{video_pk}", response_class=HTMLResponse)
async def get_video(request: Request, video_pk: int):
    return templates.TemplateResponse("index.html", {"request": request, "path": video_pk})