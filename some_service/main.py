"""Some Service's main module containing FastAPI app instance."""

import logging
import sys

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .routers import root_router, functional_router
from .async_log import init_logger, log_queue, configure_logger
from .exceptions import validation_exception_handler


description = """
Some Service API provides a sample of python FastAPI functionality in its
most basic form.

## Usage

Service can be used in two ways:
1. get server state by GET'ing root route
2. get environment variable MESSAGE_VALUE from server by GET'ing api route


### Notes

Since this code is being run upon start of the service, it's possible to format
description and add additional data to the OpenAPI's generated docs:

|Platform|Python version|
|-|-|
|{}|Python {}.{}.{}|

""".format(sys.platform, *sys.version_info[:3])

async def initialize():
    await init_logger(log_queue, address="http://127.0.0.1:8001/")


app = FastAPI(title="Some Service", description=description)
app.add_event_handler("startup", initialize)

app.include_router(root_router)
app.include_router(functional_router, prefix="/api")

app.add_exception_handler(404, validation_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

configure_logger(logging.getLogger("uvicorn.error"), queue=log_queue, stream=False)
configure_logger(logging.getLogger("uvicorn.access"), queue=log_queue, stream=False)
