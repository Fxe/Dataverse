import os
import sys
from pathlib import Path

import pytest

from src.utils.data_handlers.arm_handler import ARMHandler
from test.config_loader import Config


@pytest.fixture(scope="module")
def setup_and_teardown():
    caller_filename_full = Path(__file__).resolve()
    test_dir = caller_filename_full.parents[3]

    test_config_file = os.path.join(test_dir, 'test.cfg')
    with open(test_config_file, 'rb') as cfgfile:
        cfg = Config(cfgfile)

    cfg.print_config(sys.stdout)

    yield cfg.arm_username, cfg.arm_auth_token


def test_init(setup_and_teardown):
    arm_username, arm_auth_token = setup_and_teardown
    arm_handler = ARMHandler(arm_username, arm_auth_token)
    assert arm_handler.provider == 'ARM'
    assert arm_handler.arm_username == arm_username
    assert arm_handler.arm_auth_token == arm_auth_token


@pytest.mark.asyncio
async def test_fetch_data(setup_and_teardown):
    arm_username, arm_auth_token = setup_and_teardown
    arm_handler = ARMHandler(arm_username, arm_auth_token)
    datastream = 'sgpmetE13.b1'
    date = '2017-01-14'
    arm_data = await arm_handler.fetch_data(datastream, date)

    assert len(arm_data) == 1440

    assert 'base_time' in arm_data[0]
    assert date in arm_data[0]['base_time']
