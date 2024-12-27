from fastapi import FastAPI

from API.Routers import task

app = FastAPI()
app.include_router(task.router)
