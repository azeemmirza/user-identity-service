from src.shared.utils import verify_password_policy
from tests.conftest import parameterize, unit

@unit
@parameterize(
    'password, expected',
    [
        ("", False),
        ("1234567", False),
        ("12345678", False),
        ("long_password_123", False),
        ("StrongPass1!", True),
    ],
    ids=[
        "empty-password",
        "too-short-7-chars",
        "digits-only-8-chars",
        "missing-uppercase-and-special",
        "strong-password",
    ],
)
def test_verify_password_policy(password: str, expected: bool) -> None:
    assert verify_password_policy(password) is expected
