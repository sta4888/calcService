from fastapi import Request
from fastapi.responses import JSONResponse
from app.domain.exceptions import DomainError


def domain_exception_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
        },
    )
