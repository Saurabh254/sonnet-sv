from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import auth
from app.database.db import get_async_db
from app.drivers import models as driver_models

from . import errors, interface, schemas

router = APIRouter(tags=["Vehicle Management"], prefix="/vehicles")


@router.post(
    "/register",
    description="Register a new vehicle for the current driver.",
    response_model=schemas.VehicleProfile,
)
async def register_vehicle(
    vehicle_data: schemas.VehicleCreate,
    current_driver: driver_models.Driver = Depends(auth.get_current_driver),
    db: AsyncSession = Depends(get_async_db),
):
    return await interface.register_vehicle(vehicle_data, current_driver, db)


@router.get(
    "",
    description="Retrieve a vehicle by its ID.",
    response_model=schemas.VehicleProfile,
)
async def get_vehicle(
    current_driver: driver_models.Driver = Depends(auth.get_current_driver),
    db: AsyncSession = Depends(get_async_db),
):
    return await interface.get_vehicle(current_driver.id, db)


@router.get(
    "/nearby",
    response_model=list[schemas.VehicleProfile],
    description="Retrieve vehicles within a specified radius (default 5km) of a given location.",
)
async def get_nearby_vehicles(
    latitude: float = Query(..., description="Latitude of the reference location"),
    longitude: float = Query(..., description="Longitude of the reference location"),
    radius_km: float = Query(
        5.0, description="Radius in kilometers within which to search for vehicles"
    ),
    db: AsyncSession = Depends(get_async_db),
):
    vehicles = await interface.get_vehicles_within_radius(
        db, latitude, longitude, radius_km
    )

    return [schemas.VehicleProfile.from_orm(vehicle) for vehicle in vehicles]


@router.put(
    "/{vehicle_id}",
    description="Update vehicle details by its ID.",
    status_code=204,
)
async def update_vehicle(
    vehicle_id: str,
    vehicle_data: schemas.VehicleUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    await interface.update_vehicle(vehicle_id, vehicle_data, db)
