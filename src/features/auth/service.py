import hashlib
import ipaddress
import secrets
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status

from src.core.config import get_config
from src.core.security.jwt import decode_token, encode_token
from src.core.database.repository import BaseRepository
from src.features.auth.models.password_reset_token import PasswordResetToken
from src.features.auth.repository import PasswordResetTokenRepository
from src.features.auth.schemas import (
    ForgotPasswordRequest,
    RegisterRequest,
    ResetPasswordRequest,
    AuthResponse,
    AuthenticatedUser,
    MessageResponse,
    SessionResponse,
    TokenBundle,
    UserResponse,
    LoginRequest
)
from src.features.sessions.repository import SessionRefreshTokenRepository, SessionRepository
from src.features.sessions.models.session import Session
from src.features.sessions.models.session_refresh_token import SessionRefreshToken
from src.features.users.models.user import User
from src.features.users.repository import UserRepository
from src.shared.time import utc_now, utc_now_naive
from src.shared.utils import verify_password_policy
from src.core.security.passwords import hash_password, verify_password


config = get_config()


class AuthService:
    def __init__(
        self,
        repository: BaseRepository,
        users: UserRepository,
        sessions: SessionRepository,
        refresh_tokens: SessionRefreshTokenRepository,
        password_reset_tokens: PasswordResetTokenRepository,
    ):
        self.repository = repository
        self.users = users
        self.sessions = sessions
        self.refresh_tokens = refresh_tokens
        self.password_reset_tokens = password_reset_tokens

    async def login(self, body: LoginRequest, request: Request) -> AuthResponse:
        '''
        authenticate user and create session with refresh token

        :param db: database session
        :param body: login request body containing email, password, remember_me, and device_name
        :param request: incoming HTTP request for extracting user agent and IP address

        :return: AuthResponse containing user info, session info, and access/refresh tokens
        '''
        user = await self.users.get_by_email(body.email)
        if user is None or not verify_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid credentials",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="user account is inactive",
            )

        return await self._create_auth_response(
            user=user,
            request=request,
            remember_me=body.remember_me,
            device_name=body.device_name,
        )

    async def register(self, body: RegisterRequest, request: Request) -> AuthResponse:
        '''
        register a new user, ensuring email uniqueness and password policy compliance, then create session

        :param db: database session for querying and creating user and session records
        :param body: registration request body containing email, password, confirm_password, first_name, last_name, remember_me, and device_name
        :param request: incoming HTTP request for extracting user agent and IP address

        :return: AuthResponse containing user info, session info, and access/refresh tokens
        '''
        # validate passwords match and meet policy requirements
        self._validate_passwords(body.password, body.confirm_password)

        # normalize email for consistency and uniqueness checks
        normalized_email = self._normalize_email(body.email)
        existing_user = await self.users.get_by_email(normalized_email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="email already registered",
            )

        # determine username: use provided username if valid and unique, otherwise generate from email
        username = body.username

        if username:
            if await self.users.get_by_username(body.username):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="username already taken",
                )
            username = body.username.strip()
        else:
            username = await self._generate_username(normalized_email)

        # create user record with hashed password and active status
        user = User(
            username=username,
            email=normalized_email,
            first_name=body.first_name.strip(),
            last_name=body.last_name.strip(),
            password=hash_password(body.password),
            is_active=True,
        )
        self.users.create(user)
        await self.repository.flush()

        # if the request has session then create session else only return the user info without session and tokens
        if not body.session:
            return AuthResponse(
                user=self._serialize_user(user),
                session=None,
                tokens=None,
            )


        return await self._create_auth_response(
            user=user,
            request=request,
            remember_me=body.remember_me,
        )


    async def refresh_token(self, refresh_token: str, request: Request) -> AuthResponse:
        '''
        validate the provided refresh token, check associated session and user status, then issue new access and refresh tokens

        :param db: database session for querying sessions, users, and refresh token records
        :param refresh_token: the refresh token string provided by the client for obtaining new tokens
        :param request: incoming HTTP request for extracting user agent and IP address for session updates

        :return: AuthResponse containing user info, session info, and new access/refresh tokens if the refresh token is valid and the session/user are active; otherwise raises HTTPException with appropriate status and message
        '''
        payload = self._decode_token_payload(refresh_token, expected_type="refresh")
        session_id = self._parse_uuid(payload.get("session_id"), "invalid refresh token")
        user_id = self._parse_uuid(payload.get("sub"), "invalid refresh token")

        session = await self.sessions.get_by_id(session_id)
        user = await self.users.get_by_id(user_id)
        refresh_record = await self.refresh_tokens.get_by_session_id(session_id)

        if refresh_record is None or session is None or user is None:
            if session is not None:
                await self._revoke_session(session, revoke_tokens=False)
                await self.repository.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid refresh token",
            )

        if session.revoked_at is not None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="session is no longer active",
            )

        token_hash = self._hash_token(refresh_token)
        if refresh_record.token_hash != token_hash:
            await self._revoke_session(session, revoke_tokens=True)
            await self.repository.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="refresh token replay detected",
            )

        if refresh_record.expires_at <= self._utcnow_naive():
            await self._revoke_session(session, revoke_tokens=True)
            await self.repository.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="refresh token expired",
            )

        return await self._create_auth_response(
            user=user,
            request=request,
            remember_me=bool(session.remember_me),
            device_name=session.device_name,
            session=session,
            refresh_record=refresh_record,
        )

    async def logout(self, refresh_token: str | None, current_user: AuthenticatedUser | None ) -> MessageResponse:
        '''
        revoke the current session based on the provided refresh token or the current authenticated user, ensuring that only valid sessions can be revoked and that all associated tokens are invalidated

        :param db: database session for querying and updating session records
        :param refresh_token: optional refresh token string provided by the client to identify the session to revoke; if not provided, the current authenticated user's session will be revoked
        :param current_user: optional currently authenticated user object, used to identify the session to revoke if no refresh token is provided.

        :return: MessageResponse indicating that the session has been revoked if successful
        '''
        session: Session | None = None

        if refresh_token:
            payload = self._decode_token_payload(refresh_token, expected_type="refresh")
            session_id = self._parse_uuid(payload.get("session_id"), "invalid refresh token")
            session = await self.sessions.get_by_id(session_id)

        if session is None and current_user is not None:
            session = await self.sessions.get_by_id(current_user.session_id)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="logout requires a valid session",
            )

        await self._revoke_session(session, revoke_tokens=True)
        await self.repository.commit()
        return MessageResponse(message="session revoked")

    async def forgot_password(
        self,
        body: ForgotPasswordRequest,
    ) -> tuple[MessageResponse, str | None]:
        user = await self.users.get_by_email(body.email)
        reset_token: str | None = None
        if user is not None and user.is_active:
            reset_token = await self._create_password_reset_token(user.id)
            await self.repository.commit()

        if config.ENV == "prod":
            reset_token = None

        return (
            MessageResponse(
                message="If an account exists for that email, password reset instructions will be sent.",
            ),
            reset_token,
        )

    async def reset_password(
        self,
        body: ResetPasswordRequest,
    ) -> MessageResponse:
        self._validate_passwords(body.password, body.confirm_password)
        payload = self._decode_token_payload(body.token, expected_type="password_reset")
        reset_token_id = self._parse_uuid(payload.get("token_id"), "invalid reset token")
        user_id = self._parse_uuid(payload.get("sub"), "invalid reset token")

        reset_record = await self.password_reset_tokens.get_by_id(reset_token_id)
        user = await self.users.get_by_id(user_id)
        if reset_record is None or user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid reset token",
            )

        if reset_record.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reset token has already been used",
            )

        if reset_record.expires_at <= self._utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reset token has expired",
            )

        if reset_record.token_hash != self._hash_token(body.token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid reset token",
            )

        user.password = hash_password(body.password)
        reset_record.used_at = self._utcnow()

        active_sessions = await self.sessions.list_active_by_user_id(user.id)
        for session in active_sessions:
            await self._revoke_session(session, revoke_tokens=True)

        await self.repository.commit()
        return MessageResponse(message="password updated successfully")

    async def _create_auth_response(
        self,
        user: User,
        request: Request,
        remember_me: bool,
        device_name: str | None,
        session: Session | None = None,
        refresh_record: SessionRefreshToken | None = None,
    ) -> AuthResponse:
        if session is None:
            session = Session(
                user_id=user.id,
                user_agent=request.headers.get("user-agent"),
                ip_address=self._get_request_ip(request),
                device_name=device_name,
                remember_me=remember_me,
                last_seen_at=self._utcnow_naive(),
            )
            self.sessions.create(session)
            await self.repository.flush()
        else:
            session.user_agent = request.headers.get("user-agent") or session.user_agent
            session.ip_address = self._get_request_ip(request) or session.ip_address
            session.last_seen_at = self._utcnow_naive()

        refresh_expires_at = self._utcnow_naive() + timedelta(
            days=config.REMEMBER_ME_REFRESH_DAYS if remember_me else config.REFRESH_TOKEN_DAYS,
        )
        if refresh_record is None:
            refresh_record = SessionRefreshToken(
                session_id=session.id,
                expires_at=refresh_expires_at,
                token_hash="pending",
            )
            self.refresh_tokens.create(refresh_record)
            await self.repository.flush()
        else:
            refresh_record.expires_at = refresh_expires_at

        access_token = encode_token(
            {
                "sub": str(user.id),
                "session_id": str(session.id),
                "identity_type": "user",
                "type": "access",
            },
            expires_delta=config.ACCESS_TOKEN_MINUTES,
        )
        refresh_token = encode_token(
            {
                "sub": str(user.id),
                "session_id": str(session.id),
                "jti": secrets.token_hex(16),
                "identity_type": "user",
                "type": "refresh",
            },
            expires_delta=self._refresh_expiry_minutes(remember_me),
        )
        refresh_record.token_hash = self._hash_token(refresh_token)

        await self.repository.commit()
        await self.repository.refresh(user)
        await self.repository.refresh(session)

        return AuthResponse(
            user=self._serialize_user(user),
            session=self._serialize_session(session),
            tokens=TokenBundle(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=config.ACCESS_TOKEN_MINUTES * 60,
                refresh_expires_in=self._refresh_expiry_minutes(remember_me) * 60,
            ),
        )

    async def _create_password_reset_token(
        self,
        user_id: uuid.UUID,
    ) -> str:
        await self.password_reset_tokens.ensure_table_exists()

        reset_record = PasswordResetToken(
            user_id=user_id,
            token_hash="pending",
            expires_at=utc_now() + timedelta(minutes=config.PASSWORD_RESET_TOKEN_MINUTES),
        )
        self.password_reset_tokens.create(reset_record)
        await self.repository.flush()

        token = encode_token(
            {
                "sub": str(user_id),
                "token_id": str(reset_record.id),
                "identity_type": "user",
                "type": "password_reset",
            },
            expires_delta=config.PASSWORD_RESET_TOKEN_MINUTES,
        )
        reset_record.token_hash = self._hash_token(token)
        return token

    async def _generate_username(self, email: str) -> str:
        local_part = email.split("@", 1)[0].strip().lower() or "user"
        base_username = "".join(
            char if char.isalnum() else "_"
            for char in local_part
        ).strip("_") or "user"
        candidate = base_username[:80]
        suffix = 1

        while await self.users.get_by_username(candidate) is not None:
            suffix_text = f"_{suffix}"
            candidate = f"{base_username[:80 - len(suffix_text)]}{suffix_text}"
            suffix += 1

        return candidate

    async def _revoke_session(
        self,
        session: Session,
        *,
        revoke_tokens: bool,
    ) -> None:
        session.revoked_at = self._utcnow_naive()
        session.last_seen_at = self._utcnow_naive()

        if revoke_tokens:
            refresh_tokens = await self.refresh_tokens.list_by_session_id(session.id)
            for refresh_token in refresh_tokens:
                await self.repository.delete(refresh_token)

    def _validate_passwords(self, password: str, confirm_password: str) -> None:
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="password and confirm_password must match",
            )

        if not verify_password_policy(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "password must be at least 8 characters and include uppercase, "
                    "lowercase, digit, and special character"
                ),
            )

    def _decode_token_payload(self, token: str, *, expected_type: str) -> dict:
        try:
            payload = decode_token(token)
        except Exception as exc:  # pragma: no cover - wrapped below for API responses
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token",
            ) from exc

        if payload.get("type") != expected_type or payload.get("identity_type") != "user":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token",
            )
        return payload

    def _serialize_user(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
        )

    def _serialize_session(self, session: Session) -> SessionResponse:
        return SessionResponse(
            id=session.id,
            user_agent=session.user_agent,
            ip_address=str(session.ip_address) if session.ip_address else None,
            device_name=session.device_name,
            last_seen_at=session.last_seen_at,
            remember_me=bool(session.remember_me),
            revoked_at=session.revoked_at,
            created_at=session.created_at,
        )

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _utcnow(self) -> datetime:
        return utc_now()

    def _utcnow_naive(self) -> datetime:
        return utc_now_naive()

    def _refresh_expiry_minutes(self, remember_me: bool) -> int:
        days = config.REMEMBER_ME_REFRESH_DAYS if remember_me else config.REFRESH_TOKEN_DAYS
        return days * 24 * 60

    def _get_request_ip(self, request: Request) -> str | None:
        if request.client is None:
            return None

        try:
            return str(ipaddress.ip_address(request.client.host))
        except ValueError:
            return None

    def _parse_uuid(self, value: str | None, message: str) -> uuid.UUID:
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message,
            )
        try:
            return uuid.UUID(value)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message,
            ) from exc
