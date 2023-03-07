"""Some Service's main module containing FastAPI app instance."""

import pydantic
import sys

from fastapi import FastAPI, APIRouter

from .routers import root_router, functional_router

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

app = FastAPI(title="Some Service", description=description)


app.include_router(root_router)
app.include_router(functional_router, prefix="/api")
