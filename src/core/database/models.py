from .base import Base

# import all model modules so they register with Base
from src.modules.users.models.user import User
from src.modules.users.models.user_profile import UserProfile
from src.modules.sessions.models.session import Session
from src.modules.sessions.models.session_refresh_token import SessionRefreshToken

# expose Base/metadata for Alembic
metadata = Base.metadata
__all__ = ["Base", "metadata", "User", "UserProfile", "Session", SessionRefreshToken]
