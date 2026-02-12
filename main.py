from fastapi import FastAPI
from routers import news
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# 注册路由
app.include_router(news.router)