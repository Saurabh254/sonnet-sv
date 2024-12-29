import json
from typing import Any, Optional

from fastapi import WebSocket
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import auth
from app.exceptions import UnauthorisedUser
from app.redis_client import _redis_client
from app.users import models as user_models
from app.vehicle import interface as vehicle_interface

from . import errors, models, schemas, stream


async def login_driver(phone: str, otp: str, db: AsyncSession) -> dict[str, Any]:
    if phone[-6:] != otp:
        raise UnauthorisedUser
    stmt = select(models.Driver).where(models.Driver.phone == phone)
    result = await db.execute(stmt)
    driver = result.scalar_one_or_none()

    if not driver:
        raise errors.DriverNotFound
    access_token = auth.create_access_token(user=driver)
    return {"access_token": access_token, "driver": driver.__dict__}


async def signup_driver(
    driver_data: schemas.DriverCreate, db: AsyncSession
) -> models.Driver:
    is_existing_stmt = (
        select(func.count())
        .select_from(models.Driver)
        .filter(models.Driver.phone == driver_data.phone)
    )
    result = await db.execute(is_existing_stmt)
    count = result.scalar()
    if count:
        raise errors.DriverAlreadyExists

    driver = models.Driver(**driver_data.model_dump(exclude={"otp"}))
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver


async def logout_driver(driver: models.Driver) -> dict[str, str]:
    return {"msg": "Successfully logged out"}


async def get_driver(driver_id: str, db: AsyncSession) -> models.Driver:
    stmt = select(models.Driver).filter(models.Driver.id == driver_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_driver_from_access_token(
    token: str, db: AsyncSession
) -> Optional[models.Driver]:
    driver_id = auth.decrpt_access_token(token=token, role="Driver")
    return await get_driver(driver_id=driver_id, db=db)


async def get_driver_location(user: user_models.User, driver_id: str):
    webstream = stream.RedisStream(driver_id=driver_id)
    return webstream.get_published_messages(
        topic=stream.DRIVER_WEBSOCKET_TOPIC.format(driver_id=driver_id),
        _redis=_redis_client,
    )


def get_lat_and_long_from_websocket_data(data: str) -> tuple[float, float]:
    parsed_data = json.loads(data)
    return float(parsed_data.get("latitude")), float(parsed_data.get("longitude"))


async def handle_websocket_location_updates(websocket: WebSocket, db: AsyncSession):
    token = await websocket.receive_text()
    driver = await get_driver_from_access_token(token, db)
    if not driver:
        raise
    webstream = stream.RedisStream(driver_id=driver.id)
    while True:
        data = await websocket.receive_text()
        topic = stream.DRIVER_WEBSOCKET_TOPIC.format(driver_id=driver.id)
        await webstream.publish_data_to_topic(topic=topic, data=data)
        latitude, longitude = get_lat_and_long_from_websocket_data(data)
        await vehicle_interface.update_vehicle_location_by_driver_id(
            driver_id=driver.id, latitude=latitude, longitude=longitude, db=db
        )


async def new_ride_popup_listener(driver: models.Driver, db: AsyncSession):
    webstream = stream.RedisStream(driver_id=driver.id)
    return webstream.get_published_messages(
        topic=stream.DRIVER_EVENTSOURCE_ENDPOINT.format(driver_id=driver.id),
        _redis=_redis_client,
    )
