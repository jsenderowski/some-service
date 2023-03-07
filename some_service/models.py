"""
Module containing response models used by endpoints in the service.
"""

import pydantic

class Response(pydantic.BaseModel):
    """
    Base response model used by the service when responding to requests made
    against defined endpoints.

    :param message: string containing human-readable response data.
    """
    message: str


class DataResponse(Response):
    """
    Response class extending :class:`Response` with additional data.

    :param data: integer representing data returned by the service.
    """
    data: int
