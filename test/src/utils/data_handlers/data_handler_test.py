from src.utils.data_handlers.data_handler import DataHandler


def test_init():
    provider = 'dummy_provider'
    dh = DataHandler(provider)
    assert dh.provider == provider
