from fastapi import APIRouter, Cookie, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import auth
from app.database.db import get_async_db
from app.drivers import models as driver_models
from app.users import models as user_models

from . import interface, schemas

router = APIRouter(prefix="/drives", tags=["drives"])


@router.post("", status_code=204)
async def create_drive_endpoint(
    drive: schemas.DriveCreate,
    db: AsyncSession = Depends(get_async_db),
    user: user_models.User = Depends(auth.get_current_active_user),
):
    await interface.create_drive(user, db, drive)


@router.put("/{drive_id}", response_model=schemas.DriveUpdate)
async def update_drive_endpoint(
    drive_id: str,
    drive_update: schemas.DriveUpdate,
    db: AsyncSession = Depends(get_async_db),
    user: user_models.User = Depends(auth.get_current_active_user),
):
    return await interface.update_drive(db, drive_id, drive_update, user)


@router.delete("/{drive_id}", response_model=dict)
async def delete_drive_endpoint(
    drive_id: str,
    db: AsyncSession = Depends(get_async_db),
    user: user_models.User = Depends(auth.get_current_active_user),
):
    return await interface.delete_drive(user, db, drive_id)


@router.post("/{drive_id}/accept", response_model=dict)
async def accept_drive_endpoint(
    drive_id: str,
    db: AsyncSession = Depends(get_async_db),
    driver: driver_models.Driver = Depends(auth.get_current_driver),
):
    return await interface.accept_drive(driver, db, drive_id)


@router.post("/{drive_id}/reject", response_model=dict)
async def reject_drive_endpoint(
    drive_id: str,
    db: AsyncSession = Depends(get_async_db),
    driver: driver_models.Driver = Depends(auth.get_current_driver),
):
    return await interface.reject_drive(driver, db, drive_id)


@router.get("/{drive_id}", response_model=schemas.Drive)
async def get_drive_endpoint(
    drive_id: str,
    db: AsyncSession = Depends(get_async_db),
    user_or_driver: user_models.User | driver_models.Driver = Depends(
        auth.get_loggedin_user
    ),
):
    return await interface.get_drive_by_id(db, drive_id, user=user_or_driver)


@router.get("", response_model=list[schemas.SlimDrive])
async def get_drives_endpoint(
    db: AsyncSession = Depends(get_async_db),
    user_or_driver: user_models.User | driver_models.Driver = Depends(
        auth.get_loggedin_user
    ),
):
    if auth.is_user(user_or_driver):
        return await interface.get_drives_by_user(db, user_or_driver)
    else:

        return await interface.get_drives_by_driver(db, user_or_driver)
