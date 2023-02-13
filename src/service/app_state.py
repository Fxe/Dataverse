"""
Functions for creating and handling application state.

All functions assume that the application state has been appropriately initialized via
calling the build_app() method
"""

from fastapi import FastAPI, Request

from src.utils.config import DataverseServiceConfig
from src.utils.kbase_helpers.workspaceClient import Workspace


# The main point of this module is to handle all the stuff we add to app.state in one place
# to keep it consistent and allow for refactoring without breaking other code


async def build_app(
        app: FastAPI, cfg: DataverseServiceConfig
) -> None:
    """ Build the application state. """
    app.state._cfg = cfg
    app.state._ws_url = await _get_workspace_url(cfg)
    # allow generating the workspace client to be mocked out in a request mock
    # app.state._get_ws = lambda token: Workspace(app.state._ws_url, token=token)


async def clean_app(app: FastAPI) -> None:
    """
    Clean up the application state, shutting down external connections and releasing resources.
    """
    print("bye Dataverse")


async def _get_workspace_url(cfg: DataverseServiceConfig) -> str:
    try:
        ws = Workspace(cfg.kbase_workspace_url)
        # could check the version later if we add dependencies on newer versions
        print("Workspace version: " + ws.ver())
    except Exception as e:
        raise ValueError(f"Could not connect to workspace at {cfg.kbase_workspace_url}: {str(e)}") from e
    return cfg.kbase_workspace_url


def get_workspace_url(r: Request) -> str:
    return r.app.state._ws_url

# def get_workspace(r: Request, token: str) -> Workspace:
#     """
#     Get a workspace client initialized for a user.
#
#     r - the incoming service request.
#     token - the user's token.
#     """
#     if not r.app.state._ws_url:
#         raise ValueError("Service is running in no external connections mode")
#     return r.app.state._get_ws(token)
