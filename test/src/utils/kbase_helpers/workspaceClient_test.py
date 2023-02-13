import os
from pathlib import Path

import pytest

from src.utils.kbase_helpers.workspaceClient import Workspace
from test.config_test import TestConfig


@pytest.fixture(scope="module")
def setup_and_teardown():
    caller_filename_full = Path(__file__).resolve()
    test_dir = caller_filename_full.parents[3]

    test_config_file = os.path.join(test_dir, 'test.cfg')
    with open(test_config_file, 'rb') as cfgfile:
        cfg = TestConfig(cfgfile)

    yield cfg.kbase_workspace_url, cfg.kbase_auth_token


def test_init(setup_and_teardown):
    ws_url, auth_token = setup_and_teardown
    ws = Workspace(url=ws_url, token=auth_token)

    assert ws.ver()
