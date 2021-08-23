from fastapi import UploadFile, BackgroundTasks, HTTPException
# для генерации имени файла ипользуется библиотека uuid
from uuid import uuid4
# с помощью библиотеки shutil можно сохранять файлы
import shutil

from schema import UploadVideo
from models import Video, User

# class Video:
#     pass


async def save_video(
        user: User,
        file: UploadFile,
        title: str,
        description: str,
        back_tasks: BackgroundTasks
):
    file_name = f"media/{user.id}_{uuid4()}.mp4"
    # проверка формата видео, в случает если это не mp4 забрасывается ошибка
    if file.content_type == "video/mp4":
        # таск который выполняется на заднем фоне приложения(in this case file format validation if != mp4 raise Error)
        back_tasks.add_task(write_video, # ф-ция сохраняющая видео
                                  file_name, # путь к директории в которой файл будет сохраняться
                                  file # сохраняемый файл
                                  )
    else:
        raise HTTPException(status_code=418, detail="It isn't mp4")
    # перезаписываем загружаемый файл для его сохранения
    info = UploadVideo(title=title, description=description)
    return await Video.objects.create(file=file_name, user=user, **info.dict())



def write_video(file_name: str, file: UploadFile):
    with open(file_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


