from fastapi import FastAPI
from app.web.api import router

app = FastAPI()
app.include_router(router, prefix="/mlm")
