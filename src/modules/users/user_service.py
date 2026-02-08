from fastapi import HTTPException, status
from typing import Optional


class UserService:
    '''Service class encapsulating user operations.

    Current implementations are placeholders that raise HTTP 501 Not Implemented.
    Each method accepts an optional `db` argument for future database access.
    '''

    async def get_user(self, db: Optional[object] = None):
        # Retrieve a user (not implemented).
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )


    async def update_user(self, db: Optional[object] = None):
        # Update a user (not implemented).'''
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )


    async def delete_user(self, db: Optional[object] = None):
        # Delete a user (not implemented).'''
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )
