from datetime import datetime
import uuid

from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False
    device_name: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str
    confirm_password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool


class SessionResponse(BaseModel):
    id: uuid.UUID
    user_agent: str | None
    ip_address: str | None
    device_name: str | None
    last_seen_at: datetime | None
    remember_me: bool
    revoked_at: datetime | None
    created_at: datetime


class TokenBundle(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int


class AuthResponse(BaseModel):
    user: UserResponse
    session: SessionResponse
    tokens: TokenBundle


class AuthenticatedUser(BaseModel):
    user_id: uuid.UUID
    session_id: uuid.UUID
    identity_type: str


class MessageResponse(BaseModel):
    message: str


# register request response
class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    username: str | None = None
    session: bool = False


class RegisterResponse(BaseModel):
    user: UserResponse
    session: SessionResponse | None = None
    tokens: TokenBundle | None = None