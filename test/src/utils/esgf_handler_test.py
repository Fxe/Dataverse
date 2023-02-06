from src.utils.esgf_handler import ESGFHandler


def test_init():
    esgf_handler = ESGFHandler()
    assert esgf_handler.provider == 'ESGF'
