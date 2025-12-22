from pathlib import Path

from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from web.exception_handlers import domain_exception_handler
from domain.exceptions import DomainError
from web.routers.api import calculate
from web.routers.user import user

app = FastAPI()


BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

@app.get("/", response_class=HTMLResponse)
async def index():
    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")


app.add_exception_handler(DomainError, domain_exception_handler)

app.include_router(calculate, prefix="/mlm")
app.include_router(user, prefix="/user")
