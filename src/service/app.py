"""
API for the dataverse service.
"""

import os
import sys
from http.client import responses

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.service.routes_data import (
    ROUTER_DATA,
    SERVICE_NAME
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.common.version import VERSION
from src.service import errors, app_state
from src.service import models_errors
from src.utils.config import DataverseServiceConfig
from src.utils.timestamp import timestamp
from src.service.dataverse import Dataverse
from src.utils.data_handlers.arm_handler2 import ARMHandler2
from src.utils.data_handlers.kbase_handler2 import KBaseHandler2
from fastapi.middleware.cors import CORSMiddleware

_DATAVERSE_DEPLOYMENT_CONFIG = "DATAVERSE_DEPLOYMENT_CONFIG"

SERVICE_DESCRIPTION = "A repository of data"


def create_app(noop=False):
    """
    Create the Dataverse application
    """
    # deliberately not documenting noop, should go away when we have real tests
    if noop:
        # temporary for prototype status. Eventually need full test suite with
        # config file, all service dependencies, etc.
        return
    """
    with open(os.environ.get(_DATAVERSE_DEPLOYMENT_CONFIG, 'dataverse_config.toml'), 'rb') as cfgfile:
        cfg = DataverseServiceConfig(cfgfile)
    cfg.print_config(sys.stdout)
    sys.stdout.flush()
    """
    cfg = DataverseServiceConfig(None, "", "https://ci.kbase.us/services/ws")

    dataverse = Dataverse()
    dataverse.register_handler('ARM', ARMHandler2)
    dataverse.register_handler('KBase', KBaseHandler2)
    app_state.DATAVERSE = dataverse

    app = FastAPI(
        title=SERVICE_NAME,
        description=SERVICE_DESCRIPTION,
        version=VERSION,
        root_path=cfg.service_root_path or "",
        exception_handlers={
            errors.DataverseError: _handle_app_exception,
            RequestValidationError: _handle_fastapi_validation_exception,
            StarletteHTTPException: _handle_http_exception,
            Exception: _handle_general_exception
        },
        responses={
            "4XX": {"model": models_errors.ClientError},
            "5XX": {"model": models_errors.ServerError}
        }
    )
    app.include_router(ROUTER_DATA)

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    async def build_app_wrapper():
        await app_state.build_app(app, cfg)

    app.add_event_handler("startup", build_app_wrapper)

    async def clean_app_wrapper():
        await app_state.clean_app(app)

    app.add_event_handler("shutdown", clean_app_wrapper)
    return app


def _handle_app_exception(r: Request, exc: errors.DataverseError):
    if isinstance(exc, errors.AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, errors.UnauthorizedError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, errors.NoDataException):
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    return _format_error(status_code, exc.message, exc.error_type)


def _handle_fastapi_validation_exception(r: Request, exc: RequestValidationError):
    return _format_error(
        status.HTTP_400_BAD_REQUEST,
        error_type=errors.ErrorType.REQUEST_VALIDATION_FAILED,
        request_validation_detail=exc.errors()
    )


def _handle_http_exception(r: Request, exc: StarletteHTTPException):
    # may need to expand this in the future, mainly handles 404s
    return _format_error(exc.status_code, message=str(exc.detail))


def _handle_general_exception(r: Request, exc: Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if len(exc.args) == 1 and type(exc.args[0]) == str:
        return _format_error(status_code, exc.args[0])
    else:
        return _format_error(status_code)


def _format_error(
        status_code: int,
        message: str = None,
        error_type: errors.ErrorType = None,
        request_validation_detail=None
):
    content = {
        "httpcode": status_code,
        "httpstatus": responses[status_code],
        "time": timestamp()
    }
    if error_type:
        content.update({
            "appcode": error_type.error_code, "apperror": error_type.error_type})
    if message:
        content.update({"message": message})
    if request_validation_detail:
        content.update({"request_validation_detail": request_validation_detail})
    return JSONResponse(status_code=status_code, content=jsonable_encoder({"error": content}))
