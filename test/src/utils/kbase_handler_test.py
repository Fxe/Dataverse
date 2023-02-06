from src.utils.kbase_handler import KBaseHandler


def test_init():
    kbase_handler = KBaseHandler()
    assert kbase_handler.provider == 'KBase'
