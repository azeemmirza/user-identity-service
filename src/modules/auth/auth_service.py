from fastapi import HTTPException, status

from src.modules.auth.request_models import LoginRequest


class AuthService:
    def login(self, body: LoginRequest):

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )


    def register(self, body):
        print(body)

        return { "code": "200" }


    def logout(self):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )