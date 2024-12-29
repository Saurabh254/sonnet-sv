import json

from fastapi import (APIRouter, Body, Depends, HTTPException, WebSocket,
                     WebSocketDisconnect, WebSocketException, status)
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse

from app.auth import auth
from app.database.db import get_async_db
from app.users import models as user_models

from . import interface, models, schemas

router = APIRouter(tags=["Driver Authentication"], prefix="/drivers")


# @router.websocket("/location/ws")
# async def update_driver_location_ws_route(
#     websocket: WebSocket,
#     db: AsyncSession = Depends(get_async_db),
# ):


#     await websocket.accept()
#     try:
#     except Exception:
#         raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
active_connections: dict[str, WebSocket] = {}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, user_id: str, db: AsyncSession = Depends(get_async_db)
):
    await websocket.accept()
    token = await websocket.receive_text()
    user = await auth.get_user_from_access_token(token=token, db=db)
    if user and user.id != user_id:
        await websocket.close()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            recipient = message_data.get("recipient")
            recipient_websocket = active_connections.get(recipient)
            if recipient_websocket:
                await recipient_websocket.send_text(message_data["data"])
            else:
                await websocket.send_text(f"Recipient {recipient} is not connected.")

    except WebSocketDisconnect:
        del active_connections[user_id]


@router.get("/new_ride")
async def get_new_ride_event(
    token: str,
    db: AsyncSession = Depends(get_async_db),
):
    driver = await auth.get_user_from_access_token(token=token, db=db)
    if not auth.is_driver(driver):
        raise HTTPException(status_code=401)
    print("okkk")
    generator = await interface.new_ride_popup_listener(driver=driver, db=db)
    return EventSourceResponse(content=generator)


@router.post(
    "/login",
    description="Log in the driver with a phone number and OTP to get an access token.",
    response_model=schemas.LoginResponse,
)
async def login(
    phone: str = Body(..., description="Driver's phone number"),
    otp: str = Body(..., description="One-time password sent to the driver's phone"),
    db: AsyncSession = Depends(get_async_db),
):
    return await interface.login_driver(phone, otp, db)


@router.post(
    "/signup",
    description="Sign up a new driver using the provided data.",
    response_model=schemas.DriverProfile,
)
async def signup(
    driver_data: schemas.DriverCreate, db: AsyncSession = Depends(get_async_db)
):
    return await interface.signup_driver(driver_data=driver_data, db=db)


@router.post(
    "/logout",
    description="Logs out the currently authenticated driver and invalidates the session.",
    status_code=204,
)
async def logout(
    current_driver: models.Driver = Depends(auth.get_current_driver),
):
    await interface.logout_driver(current_driver)


@router.get(
    "/me",
    response_model=schemas.DriverProfile,
    description="Retrieve the profile of the currently authenticated driver.",
)
async def read_me(
    current_driver: models.Driver = Depends(auth.get_current_driver),
):
    return current_driver
