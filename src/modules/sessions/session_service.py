from fastapi import HTTPException, status


class SessionService:
    def get_sessions(self):
        # Retrieve a user (not implemented).
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )

    def get_session(self, session_id: str):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )

    def revoke_session(self, session_id: str):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )