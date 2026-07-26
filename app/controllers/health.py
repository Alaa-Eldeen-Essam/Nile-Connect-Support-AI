from fastapi import APIRouter, Depends

from app.dependencies import services
from app.services.application import ApplicationServices

router = APIRouter(tags=["health"])


@router.get("/healthz")
def health(app_services: ApplicationServices = Depends(services)):
    return {
        "status": "ok",
        "environment": app_services.config.app_env,
        "profile_storage": app_services.config.profile_storage,
    }
