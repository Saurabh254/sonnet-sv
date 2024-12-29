from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app import api as public_api
from app.exception_handling import add_exception_handler

app = FastAPI(
    title="Sonnet",
    description="A FastAPI application build for a purpose.",
    version="0.0.1",
    contact={
        "name": "Saurabh Vishwakarma",
        "url": "https://www.saurabhvishwakarma.in",
        "email": "contact@saurabhvishwakarma.in",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


app.include_router(public_api.router)
add_exception_handler(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["internal"],
    summary="Health Check",
    description="This endpoint checks the health status of the application and returns a message indicating if the service is operational.",
)
async def check_health():
    return {"status": "we're up"}
