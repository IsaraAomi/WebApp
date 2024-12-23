from api.routers import done, task
from fastapi import FastAPI

app = FastAPI()
app.include_router(task.router)
app.include_router(done.router)
