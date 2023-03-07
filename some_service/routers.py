import os

from fastapi import APIRouter, HTTPException
from http import HTTPStatus

from .models import Response, DataResponse

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

    environment_variable = os.getenv("MESSAGE_VALUE")

    if environment_variable is None:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail="MESSAGE_VALUE envirionment variable not set")

    return DataResponse(message=environment_variable, data=api_call_count)
