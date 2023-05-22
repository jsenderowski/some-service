import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from .models import Response

from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.exception("Something went bad", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content="Internal server error",
    )
