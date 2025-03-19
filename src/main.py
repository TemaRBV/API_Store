from fastapi import FastAPI
from endpoints import router
import uvicorn

app = FastAPI()

app.include_router(router)

