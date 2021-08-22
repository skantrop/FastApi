from fastapi import FastAPI
from api import video_router


app = FastAPI()

# подключаем router который находиться в файле app
# чтобы функции прописанные там работали и FastAPI их мог обрабатывать
# таким образом мы подключили эти url к основному приложению
app.include_router(video_router)

