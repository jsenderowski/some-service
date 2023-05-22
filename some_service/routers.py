import os
import logging

from fastapi import APIRouter, HTTPException
from http import HTTPStatus

from .models import Response, DataResponse

from .async_log import task_id

root_router = APIRouter(tags=["root"])

@root_router.get("/", response_model=Response)
async def root():
    """
    Root endpoint of *Some Service*.

    OpenAPI supports `Markdown` which can be easily passed by docstring
    of defined method function.
    """
    return Response(message="Server OK")


functional_router = APIRouter(prefix="/v1", tags=["functional API"])

api_call_count = 0
"""count of GET requests to /getSomeData endpoint"""

@functional_router.get("/getSomeData", response_model=DataResponse)
async def get_some_data():

    """
    Functional endpoint of `some-service` used for requesting
    data provided by the service.

    Returns `MESSAGE_VALUE` environment variable value and count of GET requests
    to this API route.
    """
    global api_call_count
    api_call_count += 1

    logging.info(f"API call ({api_call_count}) {await task_id()}")

    return DataResponse(message="test", data=api_call_count)
