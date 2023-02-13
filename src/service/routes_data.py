"""
Routes for general dataverse endpoints
"""

from typing import Any, Optional

from fastapi import APIRouter, Request, Header, Path
from pydantic import BaseModel, Field

from src.common.version import VERSION
from src.service import app_state
from src.service.errors import MissingTokenError, IllegalParameterError
from src.utils.data_handlers.kbase_handler import KBaseHandler
from src.utils.timestamp import timestamp

SERVICE_NAME = "ESS Dataverse"

ROUTER_DATA = APIRouter(tags=["Data"])

PROVIDERS = ["KBase", "ESGF", "ARM"]

_PATH_PROVIDER = Path(
    default="KBase",
    example="KBase",
    description="Data provider"
)

_HEADER_REF = Header(
    default=None,
    example="101147/7",
    description="Object reference",
    alias="Object-Reference"
)

_HEADER_KBASE_AUTH_TOKEN = Header(
    default=None,
    description="KBase authentication token",
    alias="KBase-Auth-Token"
)


class Root(BaseModel):
    service_name: str = Field(example=SERVICE_NAME)
    version: str = Field(example=VERSION)
    server_time: str = Field(example="2022-10-07T17:58:53.188698+00:00")


class RetrievedData(BaseModel):
    metadata: Optional[Any] = Field(example=["object_name", "object_version"])
    data: Optional[Any] = Field(example={"object_data_field": "object_data"})


@ROUTER_DATA.get("/", response_model=Root, include_in_schema=False)
async def root():
    return {
        "service_name": SERVICE_NAME,
        "version": VERSION,
        "server_time": timestamp()
    }


@ROUTER_DATA.get("/data/{provider}", response_model=RetrievedData)
async def retrieve_data(r: Request,
                        provider: str = _PATH_PROVIDER,
                        object_reference: str = _HEADER_REF,
                        kbase_auth_token: str = _HEADER_KBASE_AUTH_TOKEN) -> RetrievedData:
    metadata, data = list(), dict()

    if provider not in PROVIDERS:
        raise IllegalParameterError(f'Unexpected provider. Please use one of {PROVIDERS}')

    if provider == 'KBase':
        ws_url = app_state.get_workspace_url(r)
        if not kbase_auth_token:
            raise MissingTokenError('Please provide KBase Auth Token')

        kbase_handler = KBaseHandler(kbase_auth_token, ws_url=ws_url)
        metadata, data = await kbase_handler.fetch_data(object_reference)

    return RetrievedData(metadata=metadata, data=data)
