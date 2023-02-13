import os
import sys
from pathlib import Path

import pytest
import asyncio

from src.utils.data_handlers.kbase_handler import KBaseHandler
from test.config_loader import Config


@pytest.fixture(scope="module")
def setup_and_teardown():
    caller_filename_full = Path(__file__).resolve()
    test_dir = caller_filename_full.parents[3]

    test_config_file = os.path.join(test_dir, 'test.cfg')
    with open(test_config_file, 'rb') as cfgfile:
        cfg = Config(cfgfile)

    cfg.print_config(sys.stdout)

    yield cfg.kbase_workspace_url, cfg.kbase_auth_token


def test_init(setup_and_teardown):
    ws_url, auth_token = setup_and_teardown
    kbase_handler = KBaseHandler(auth_token, ws_url=ws_url)
    assert kbase_handler.provider == 'KBase'
    assert kbase_handler.auth_token == auth_token


@pytest.mark.asyncio
async def test_fetch_data(setup_and_teardown):
    ws_url, auth_token = setup_and_teardown
    kbase_handler = KBaseHandler(auth_token, ws_url=ws_url)
    pointer = '101147/7'  # public narrative https://narrative.kbase.us/narrative/101147
    obj_info, obj_data = await kbase_handler.fetch_data(pointer)

    assert obj_info[1] == 'Ath_hy5_R1'
    assert 'KBaseFile.SingleEndLibrary' in obj_info[2]

    assert 'gc_content' in obj_data


@pytest.mark.asyncio
async def test_save_data(setup_and_teardown):
    ws_url, auth_token = setup_and_teardown

    kbase_handler = KBaseHandler(auth_token, ws_url=ws_url)

    obj_data = {
        'type': 'Empty.AType',
        'name': 'test_obj',
        'data': {'foo': 15}
    }
    wsid = 45460  # TODO: create a test workspace and use that instead

    obj_info, obj_ref = await kbase_handler.save_data(wsid, obj_data)

    assert obj_info[1] == 'test_obj'
    assert 'Empty.AType' in obj_info[2]

    assert obj_ref.split('/')[0] == str(wsid)
