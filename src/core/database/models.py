from .base import Base

# import all model modules so they register with Base
from src.features.users.models.user import User
from src.features.users.models.user_profile import UserProfile
from src.features.sessions.models.session import Session
from src.features.sessions.models.session_refresh_token import SessionRefreshToken
from src.features.auth.models.password_reset_token import PasswordResetToken

# expose Base/metadata for Alembic
metadata = Base.metadata
__all__ = [
    "Base",
    "metadata",
    "User",
    "UserProfile",
    "Session",
    "SessionRefreshToken",
    "PasswordResetToken",
]
