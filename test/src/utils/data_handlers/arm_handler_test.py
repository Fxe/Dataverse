from src.utils.data_handlers.arm_handler import ARMHandler


def test_init():
    arm_handler = ARMHandler()
    assert arm_handler.provider == 'ARM'
