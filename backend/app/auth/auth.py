from datetime import datetime, timedelta
from typing import Annotated, Any, Literal, Optional, Union

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_bearer import JWTBearer
from app.database.db import get_async_db
from app.drivers import interface as driver_interface
from app.drivers import models as driver_models
from app.exceptions import UnauthorisedUser
from app.users import interface as user_interface
from app.users import models as user_models

SECRET_KEY = "8cbfecba4cd7d500fdd63917cbe3ce517f0d72946d9e9f7f5e7820d74fb38082"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def is_user(user: Union[user_models.User, driver_models.Driver]) -> bool:
    return isinstance(user, user_models.User)


def is_driver(user: Union[user_models.User, driver_models.Driver]) -> bool:
    return isinstance(user, driver_models.Driver)


def get_user_type(user: Union[user_models.User, driver_models.Driver]) -> str:
    type = None
    if isinstance(user, user_models.User):
        type = "User"
    elif isinstance(user, driver_models.Driver):
        type = "Driver"

    return type


def create_access_token(
    user: Union[user_models.User, driver_models.Driver],
    expires_delta: Union[timedelta, None] = None,
) -> str:
    to_encode = {"id": user.id, "role": get_user_type(user)}

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})  # type: ignore
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decrpt_access_token(token: str, role: Literal["User", "Driver"]) -> str:
    user_id = None  # type: ignore
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")  # type: ignore
        _role: str = payload.get("role")  # type: ignore
        if _role != role:
            raise
    except (JWTError, Exception):
        pass
    return user_id


async def get_optional_loggedin_user(
    token: Annotated[str, Depends(JWTBearer(auto_error=False))],
    db: AsyncSession = Depends(get_async_db),
) -> Union[user_models.User, driver_models.Driver, None]:
    user_id = None  # type: ignore
    role = None  # type: ignore
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")  # type: ignore
        role: str = payload.get("role")  # type: ignore
    except (JWTError, Exception):
        pass
    user = None
    if user_id:
        if role == "User":
            user = await user_interface.get_user(user_id=user_id, db=db)
        elif role == "Driver":
            user = await driver_interface.get_driver(driver_id=user_id, db=db)
    return user


async def get_loggedin_user(
    optional_user: Annotated[
        Optional[Union[user_models.User, driver_models.Driver]],
        Depends(get_optional_loggedin_user),
    ]
) -> Union[user_models.User, driver_models.Driver]:

    if optional_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return optional_user


async def get_current_user(
    loggedin_user: Annotated[
        user_models.User | driver_models.Driver | None, Depends(get_loggedin_user)
    ],
) -> user_models.User:

    if is_user(loggedin_user):
        return loggedin_user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized."
        )


async def get_current_active_user(
    user: Any = Depends(get_current_user),
) -> user_models.User:
    if user.active:
        return user
    raise UnauthorisedUser(message="forbidden user")


async def get_current_driver(
    loggedin_user: Annotated[
        user_models.User | driver_models.Driver | None, Depends(get_loggedin_user)
    ],
) -> driver_models.Driver:
    if is_driver(loggedin_user):
        return loggedin_user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized."
        )


async def get_user_from_access_token(
    token: str, db: AsyncSession
) -> user_models.User | driver_models.Driver:
    user_id = None
    role = None  # type: ignore
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")  # type: ignore
        role: str = payload.get("role")  # type: ignore

    except (JWTError, Exception):
        pass
    if role == "Driver":
        return await driver_interface.get_driver(driver_id=user_id, db=db)
    elif role == "User":
        return await user_interface.get_user(user_id=user_id, db=db)
    else:
        raise
