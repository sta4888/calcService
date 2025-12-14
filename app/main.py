from fastapi import FastAPI
from web.api import router
from web.exception_handlers import domain_exception_handler
from domain.exceptions import DomainError

app = FastAPI()

app.add_exception_handler(DomainError, domain_exception_handler)

app.include_router(router, prefix="/mlm")
