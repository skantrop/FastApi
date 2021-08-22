from fastapi import FastAPI
from api import video_router
from db import database, metadata, engine

app = FastAPI()
# подключение ORM ormar(file db.py)
# связываем базу данных с приложением
metadata.create_all(engine)
app.state.database = database


# проверка подключенности базы данных во время запуска программы
@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected: # проверка на подключенность дб
        await database_.connect() # если не подключено, подключить


# проверка разрыва подключения базы данных перед закрытием программы
@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected: # проверка на подключенность
        await database_.disconnect() # если подключено отключить

# подключаем router который находиться в файле app
# чтобы функции прописанные там работали и FastAPI их мог обрабатывать
# таким образом мы подключили эти url к основному приложению
app.include_router(video_router)

