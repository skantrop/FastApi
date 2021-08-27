# с помощью библиотеки shutil можно сохранять файлы
import shutil
import ormar
from pathlib import Path
from typing import IO, Generator
# для генерации имени файла ипользуется библиотека uuid
from uuid import uuid4

import aiofiles
from fastapi import UploadFile, BackgroundTasks, HTTPException
from starlette.requests import Request

from models import Video, User
from schema import UploadVideo
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


# ф-ция разделения видео по байтам чтобы можно было порционно прогружать видео,
# для меньшего времени ожидания выгрузки полного файла и его воспроизведения
def ranged(
        file: IO[bytes],
        start: int = 0,
        end: int = None,
        block_size: int = 8192,
) -> Generator[bytes, None, None]:
    consumed = 0

    file.seek(start)
    while True:
        data_length = min(block_size, end - start - consumed) if end else block_size
        if data_length <= 0:
            break
        data = file.read(data_length)
        if not data:
            break
        consumed += data_length
        yield data

    if hasattr(file, 'close'):
        file.close()


async def open_file(request: Request, video_pk: int) -> tuple:
    try:
        # получить видео из БД чтобы получить его адрес
        file = await Video.objects.get(pk=video_pk)
    except ormar.exceptions.NoMatch:
        # если такое видео не будет найдено в БД генерируется исключение
        # ошибка о несоответствии введенных данных
        raise HTTPException(status_code=404, detail="Not found")
    path = Path(file.dict().get('file')) # переходим в директорию
    file = path.open('rb') # открываем файл
    file_size = path.stat().st_size # и считываем объем файла

    # дефолтные значения размера файла, статус код 200, пустой headers и длина контента
    # возвращаемые в случае если content_range is None
    content_length = file_size
    status_code = 200
    headers = {}
    content_range = request.headers.get('range')

    if content_range is not None:
        # разделяем видео на потоки чтобы можно было его перематывать
        content_range = content_range.strip().lower() # общая продолжительность
        content_ranges = content_range.split('=')[-1]
        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1 # конечная точка воспрооизведения
        content_length = (range_end - range_start) + 1  # длина контента
        file = ranged(file, start=range_start, end=range_end + 1)
        status_code = 206 # Partial Content success status
        headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

    return file, status_code, content_length, headers