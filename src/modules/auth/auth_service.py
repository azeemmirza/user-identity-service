from fastapi import HTTPException, status


class AuthService:
    def login(self):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )

    def logout(self):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )

    def register(self):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )