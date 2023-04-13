from fastapi import Path, Header, Query
from pydantic import BaseModel

PROVIDERS = ["KBase", "ESGF", "ARM"]


class RequestObject(BaseModel):
    object_id: str | None = None
    date_end: str | None = None
    date_start: str | None = None
    version: int | None = None


PATH_PROVIDER = Path(
    #default="KBase",
    example="KBase",
    description=f"Data provider from one of the following options: {PROVIDERS}."
)

HEADER_KBASE_AUTH_TOKEN = Header(
    default=None,
    description="KBase authentication token",
    alias="KBase-Auth-Token"
)

HEADER_ARM_AUTH_TOKEN = Header(
    default=None,
    description="The access token for accessing the ADC archive.",
    alias="ARM-Auth-Token"
)

HEADER_AUTH_TOKEN = Header(
    default=None,
    description="Auth token",
    alias="Auth-Token"
)

HEADER_ARM_USERNAME = Header(
    default=None,
    description="Auth user",
    alias="Username"
)

KBASE_OBJ_REF = Query(
    default=None,
    example="101147/7",
    description="KBase object reference"
)

ARM_DATASREAM = Query(
    default=None,
    example="sgpmetE13.b1",
    description="The name of the datastream to acquire from ARM"
)

ARM_ACQ_DATE = Query(
    default=None,
    example="2017-01-14",
    regex=r'^\d{4}-\d{2}-\d{2}$',
    description="The date of data to acquire from ARM"
)
