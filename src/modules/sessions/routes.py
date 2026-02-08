from fastapi import APIRouter

from src.modules.sessions.session_service import SessionService


router = APIRouter()
service = SessionService()

@router.get('/')
async def get_sessions():
    return service.get_sessions()


@router.get('/{session_id}')
async def get_session(session_id: str):
    return service.get_session(session_id)


@router.delete('/{session_id}')
async def revoke_session(session_id: str):
    return service.revoke_session(session_id)