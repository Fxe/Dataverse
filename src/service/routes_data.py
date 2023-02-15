"""
Routes for general dataverse endpoints
"""
from typing import Any, Optional

from fastapi import APIRouter, Request, Body
from pydantic import BaseModel, Field

import src.common.common_params as common_params
from src.common.version import VERSION
from src.service import app_state
from src.service.errors import MissingTokenError, IllegalParameterError, MissingParameterError
from src.utils.data_handlers.arm_handler import ARMHandler
from src.utils.data_handlers.kbase_handler import KBaseHandler
from src.utils.timestamp import timestamp

SERVICE_NAME = "ESS Dataverse"

ROUTER_DATA = APIRouter(tags=["Data"])


class Obj(BaseModel):
    type: str = Field(example="Empty.AType")
    name: str = Field(example="test_obj")
    data: dict = Field(example={"foo": 15})


class ObjToSave(BaseModel):
    wsid: int = Field(example=45460)
    obj_data: Obj
    provenance: Optional[list]


class Root(BaseModel):
    service_name: str = Field(example=SERVICE_NAME)
    version: str = Field(example=VERSION)
    server_time: str = Field(example="2022-10-07T17:58:53.188698+00:00")


class RetrievedData(BaseModel):
    kbase_metadata: Optional[Any] = Field(example=["object_name", "object_version"])
    kbase_data: Optional[Any] = Field(example={"object_data_field": "object_data"})
    arm_data: Optional[Any] = Field(example={"object_data_field": "object_data"})


class SavedData(BaseModel):
    kbase_obj_ref: Optional[str] = Field(example="101147/7")
    kbase_obj_info: Optional[list[Any]] = Field(example=["object_name", "object_version"])


@ROUTER_DATA.get("/", response_model=Root, include_in_schema=False)
async def root():
    return {
        "service_name": SERVICE_NAME,
        "version": VERSION,
        "server_time": timestamp()
    }


@ROUTER_DATA.get("/data/{provider}", response_model=RetrievedData)
async def retrieve_data(r: Request,
                        provider: str = common_params.PATH_PROVIDER,
                        kbase_object_reference: Optional[str] = common_params.KBASE_OBJ_REF,
                        arm_datastream: Optional[str] = common_params.ARM_DATASREAM,
                        arm_acquire_date: Optional[str] = common_params.ARM_ACQ_DATE,
                        kbase_auth_token: Optional[str] = common_params.HEADER_KBASE_AUTH_TOKEN,
                        arm_auth_token: Optional[str] = common_params.HEADER_ARM_AUTH_TOKEN,
                        arm_username: Optional[str] = common_params.HEADER_ARM_USERNAME) -> RetrievedData:
    kbase_metadata, kbase_data, arm_data = list(), dict(), list()

    if provider == 'KBase':
        ws_url = app_state.get_workspace_url(r)
        if not kbase_auth_token:
            raise MissingTokenError('Please provide KBase Auth Token')

        kbase_handler = KBaseHandler(kbase_auth_token, ws_url=ws_url)

        if not kbase_object_reference:
            raise MissingParameterError('Please provide KBase Object Reference')
        kbase_metadata, kbase_data = await kbase_handler.fetch_data(kbase_object_reference)

    elif provider == 'ARM':
        if not (arm_username and arm_auth_token):
            raise MissingTokenError('Please provide ARM Auth Token and Username')
        arm_handler = ARMHandler(arm_username, arm_auth_token)

        if not (arm_datastream and arm_acquire_date):
            raise MissingParameterError('Please provide ARM Datastream and Acquire Date')
        arm_data = await arm_handler.fetch_data(arm_datastream, arm_acquire_date)
    elif provider == 'ESGF':
        pass
    else:
        raise IllegalParameterError(f'Unexpected provider. Please use one of {common_params.PROVIDERS}')

    return RetrievedData(kbase_metadata=kbase_metadata, kbase_data=kbase_data, arm_data=arm_data)


@ROUTER_DATA.post("/data/{provider}", response_model=SavedData)
async def save_data(r: Request,
                    provider: str = common_params.PATH_PROVIDER,
                    save_obj: ObjToSave = Body(...),
                    kbase_auth_token: Optional[str] = common_params.HEADER_KBASE_AUTH_TOKEN) -> SavedData:
    kbase_obj_ref, kbase_obj_info = list(), None

    if provider == 'KBase':
        ws_url = app_state.get_workspace_url(r)
        if not kbase_auth_token:
            raise MissingTokenError('Please provide KBase Auth Token')

        kbase_handler = KBaseHandler(kbase_auth_token, ws_url=ws_url)

        wsid, obj_data, provenance = save_obj.wsid, save_obj.obj_data, save_obj.provenance

        kbase_obj_ref, kbase_obj_info = await kbase_handler.save_data(wsid, obj_data.dict(), provenance=provenance)

    elif provider == 'ARM':
        pass

    elif provider == 'ESGF':
        pass

    else:
        raise IllegalParameterError(f'Unexpected provider. Please use one of {common_params.PROVIDERS}')

    return SavedData(kbase_obj_ref=kbase_obj_ref, kbase_obj_info=kbase_obj_info)
