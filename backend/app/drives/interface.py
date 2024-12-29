import random
from operator import or_
from typing import Sequence

import googlemaps
from fastapi import HTTPException
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app import config
from app.auth import auth
from app.drivers import models as driver_models
from app.drivers import stream as driver_stream
from app.users import models as user_models
from app.vehicle.interface import wkb_to_dict

from .models import (  # Adjust the import according to your project structure
    Drive, DriveStatus)
from .schemas import (  # Assuming you have Pydantic models in schemas.py
    DriveCreate, DriveUpdate)


async def create_drive(
    user: user_models.User, db: AsyncSession, drive_create: DriveCreate
) -> Drive:
    new_drive = Drive(
        **{
            **drive_create.model_dump(exclude={"user_id", "location"}),
            "user_id": user.id,
            "pickup_location": f"SRID=4326;POINT({drive_create.pickup_location.longitude} {drive_create.pickup_location.latitude})",
            "dropoff_location": f"SRID=4326;POINT({drive_create.dropoff_location.longitude} {drive_create.dropoff_location.latitude})",
        }
    )
    db.add(new_drive)
    await db.commit()


def calculate_distance(pickup, dropoff):
    # Implement your logic to calculate distance
    return round(random.uniform(1.0, 50.0), 2)


def calculate_estimated_time(distance):
    # Implement your logic for estimating time based on distance
    return round(distance / random.uniform(30, 60) * 60)


def calculate_fare(distance):
    # Implement your logic for calculating fare
    return round(distance * random.uniform(1.5, 3.5), 2)


async def stream_sse_to_driver(new_drive: Drive, user: user_models.User):

    distance = calculate_distance(new_drive.pickup_location, new_drive.dropoff_location)
    estimated_time = calculate_estimated_time(
        distance
    )  # You might define this function
    fare = calculate_fare(distance)  # You might define this function

    passenger_name = user.name  # Assuming the User model has a name attribute
    passenger_contact = user.contact  # Assuming the User model has a contact attribute

    # Prepare data to send as an event
    data = {
        "pickupLocation": to_shape(new_drive.pickup_location),
        "dropoffLocation": to_shape(new_drive.dropoff_location),
        "distance": distance,
        "estimatedTime": estimated_time,
        "fare": fare,
        "passengerName": passenger_name,
        "passengerContact": passenger_contact,
    }
    await create_new_ride_notification(driver_id=new_drive.driver_id, data=data)


async def update_drive(
    db: AsyncSession,
    drive_id: str,
    drive_update: DriveUpdate,
    user: user_models.User,
) -> Drive:
    stmt = select(Drive).where(Drive.id == drive_id).where(Drive.user_id == user.id)
    result = await db.execute(stmt)
    drive = result.scalar_one_or_none()
    if drive is None:
        raise HTTPException(status_code=404, detail="Drive not found")

    for key, value in drive_update.dict().items():
        if key == "dropoff_location" or key == "pickup_location":
            setattr(
                drive,
                key,
                f"SRID=4326;POINT({value.longitude} {value.latitude})",
            )
        else:
            setattr(drive, key, value)

    await db.commit()
    await db.refresh(drive)
    return drive


async def delete_drive(user: user_models.User, db: AsyncSession, drive_id: str) -> dict:
    stmt = select(Drive).where(Drive.id == drive_id).where(Drive.user_id == user.id)
    result = await db.execute(stmt)
    drive = result.scalar_one_or_none()
    if drive is None:
        raise HTTPException(status_code=404, detail="Drive not found")

    await db.delete(drive)
    await db.commit()
    return {"detail": "Drive deleted successfully"}


async def accept_drive(
    driver: driver_models.Driver, db: AsyncSession, drive_id: str
) -> dict:
    stmt = select(Drive).where(Drive.id == drive_id).where(Drive.user_id == driver.id)
    result = await db.execute(stmt)
    drive = result.scalar_one_or_none()
    if drive is None:
        raise HTTPException(status_code=404, detail="Drive not found")

    drive.status = DriveStatus.ACCEPTED  # type: ignore
    await db.commit()
    return {"detail": "Drive accepted successfully"}


async def reject_drive(
    driver: driver_models.Driver, db: AsyncSession, drive_id: str
) -> dict:
    stmt = select(Drive).filter(Drive.id == drive_id).where(Drive.user_id == driver.id)
    result = await db.execute(stmt)
    drive = result.scalar_one_or_none()
    if drive is None:
        raise HTTPException(status_code=404, detail="Drive not found")

    drive.status = DriveStatus.REJECTED  # type: ignore
    await db.commit()
    return {"detail": "Drive rejected successfully"}


async def get_drive_by_id(
    db: AsyncSession, drive_id: str, user: user_models.User | driver_models.Driver
) -> dict | None:
    stmt = (
        select(Drive)
        .options(
            joinedload(Drive.user), joinedload(Drive.driver), joinedload(Drive.vehicle)
        )
        .where(Drive.id == drive_id)
        .where(or_(Drive.user_id == user.id, Drive.driver_id == user.id))
    )
    result = await db.execute(stmt)
    drive = result.scalar_one_or_none()

    if not drive:
        return None
    # Convert pickup and dropoff locations to dictionaries
    pickup_location = to_shape(drive.pickup_location)  # type: ignore
    dropoff_location = to_shape(drive.dropoff_location)  # type: ignore
    if drive.vehicle:
        # Convert the location to a dictionary
        vehicle_dict = (
            drive.vehicle.__dict__.copy()
        )  # Copy the vehicle's attributes to a dict
        vehicle_dict["location"] = wkb_to_dict(
            drive.vehicle.location
        )  # Convert the location
    drive_data = {
        "id": drive.id,
        "driver_id": drive.driver_id,
        "pickup_location": {
            "latitude": pickup_location.y,
            "longitude": pickup_location.x,
        },
        "dropoff_location": {
            "latitude": dropoff_location.y,
            "longitude": dropoff_location.x,
        },
        "status": drive.status,  # Assuming status is an enum
        "user": drive.user,  # You can include user details here
        "driver": drive.driver,  # You can include user details here
        "created_at": drive.created_at,
        "updated_at": drive.updated_at,
        "vehicle": vehicle_dict,
    }

    return drive_data


async def get_drives_by_driver(
    db: AsyncSession, driver: driver_models.Driver
) -> Sequence[Drive]:
    stmt = (
        select(Drive)
        .options(
            joinedload(Drive.user),
        )
        .where(Drive.driver_id == driver.id)
        .order_by(Drive.created_at)
    )
    result = await db.execute(stmt)
    drives = result.scalars().all()
    return drives


async def get_drives_by_user(
    db: AsyncSession, user: user_models.User
) -> Sequence[Drive]:
    stmt = select(Drive).where(Drive.user_id == user.id).order_by(Drive.created_at)
    result = await db.execute(stmt)
    drives = result.scalars().all()
    return drives


# const rideDetails = {
#         pickupLocation: '123 Main St, San Francisco, CA',
#         dropoffLocation: '456 Oak St, Oakland, CA',
#         distance: 12.4, // distance in kilometers
#         estimatedTime: 18, // estimated time in minutes
#         fare: 27.50, // fare in USD
#         passengerName: 'Jane Doe',
#         passengerContact: '+1 (555) 123-4567',
#     };


gmaps = googlemaps.Client(key=config.GOOGLE_MAPS_API_KEY)


def get_ride_details(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng):
    pickup_location = gmaps.reverse_geocode((pickup_lat, pickup_lng))[0][  # type: ignore
        "formatted_address"
    ]
    dropoff_location = gmaps.reverse_geocode((dropoff_lat, dropoff_lng))[0][  # type: ignore
        "formatted_address"
    ]

    result = gmaps.distance_matrix(  # type: ignore
        origins=f"{pickup_lat},{pickup_lng}",
        destinations=f"{dropoff_lat},{dropoff_lng}",
        mode="driving",
    )

    distance = result["rows"][0]["elements"][0]["distance"]["value"] / 1000
    duration = result["rows"][0]["elements"][0]["duration"]["value"] / 60

    # Base fare remains the same
    base_fare = 5.0

    # Apply tiered pricing based on distance
    if distance < 5:
        per_km_rate = 5.0 * 1000  # Higher rate for short trips
    elif 5 <= distance <= 15:
        per_km_rate = 2.0  # Moderate rate for medium trips
    else:
        per_km_rate = 1.5  # Lower rate for long trips

    fare = base_fare + (distance * per_km_rate)

    passenger_name = "Jane Doe"
    passenger_contact = "+1 (555) 123-4567"

    ride_details = {
        "pickupLocation": pickup_location,
        "dropoffLocation": dropoff_location,
        "distance": round(distance, 2),
        "estimatedTime": round(duration),
        "fare": round(fare, 2),
        "passengerName": passenger_name,
        "passengerContact": passenger_contact,
    }

    return ride_details


async def create_new_ride_notification(driver_id: str, data):
    webstream = driver_stream.RedisStream(driver_id=driver_id)
    topic = driver_stream.DRIVER_EVENTSOURCE_ENDPOINT.format(driver_id)
    await webstream.publish_data_to_topic(topic, data)
