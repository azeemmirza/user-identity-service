from fastapi import APIRouter
from fastapi_cloud_cli.commands import login

router = APIRouter()

@router.get('/')
async def get_user():
    return NotImplementedError()


@router.put('/')
async def update_user():
    return NotImplementedError()


@router.delete('/')
async def delete_user():
    return NotImplementedError()