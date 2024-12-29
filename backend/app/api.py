from fastapi import APIRouter

from app.drivers import api as driver_api
from app.drives import api as drive_api
from app.users import api as users_api
from app.vehicle import api as vehicle_api

router = APIRouter(prefix="/api/v1")

router.include_router(users_api.router)
router.include_router(vehicle_api.router)
router.include_router(driver_api.router)
router.include_router(drive_api.router)
