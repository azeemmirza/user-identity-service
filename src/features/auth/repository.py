import uuid

from src.core.database.repository import BaseRepository
from src.features.auth.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository(BaseRepository):
    async def get_by_id(self, token_id: uuid.UUID) -> PasswordResetToken | None:
        return await self.get(PasswordResetToken, token_id)

    def create(self, reset_token: PasswordResetToken) -> PasswordResetToken:
        self.add(reset_token)
        return reset_token

    async def ensure_table_exists(self) -> None:
        connection = await self.connection()
        await connection.run_sync(
            lambda sync_connection: PasswordResetToken.__table__.create(
                bind=sync_connection,
                checkfirst=True,
            ),
        )
