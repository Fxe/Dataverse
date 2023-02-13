from io import BytesIO

from src.utils.config import DataverseServiceConfig


def test_config_minimal():
    cfg = DataverseServiceConfig(
        BytesIO("\n".join([
            "[Service]",
            "[Service_Dependencies]",
            'kbase_workspace_url="whee"'
        ]).encode('utf-8')))

    assert cfg.service_root_path is None
    assert cfg.kbase_workspace_url == "whee"
