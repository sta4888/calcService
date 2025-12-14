from fastapi import FastAPI
from web.exception_handlers import domain_exception_handler
from domain.exceptions import DomainError
from web.routers.api import claculate
from web.routers.user import user

app = FastAPI()

app.add_exception_handler(DomainError, domain_exception_handler)

app.include_router(claculate, prefix="/mlm")
app.include_router(user, prefix="/user")
