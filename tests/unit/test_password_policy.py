import pytest

from src.shared.utils import verify_password_policy

unittest = pytest.mark.unit
unit_parameterize = pytest.mark.parametrize

@unittest
@unit_parameterize(
    'password, expected',
    [
        ("", False),
        ("1234567", False),
        ("12345678", True),
        ("long_password_123", True)
    ],
    ids=[
        "empty-password",
        "too-short-7-chars",
        "min-length-8-chars",
        "long-valid-password",
    ],
)
def test_verify_password_policy(password: str, expected: bool) -> None:
    assert verify_password_policy(password) is expected