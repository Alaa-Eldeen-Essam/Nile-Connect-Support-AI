from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.dependencies import services
from app.models.schemas import RuntimeSettingsUpdate
from app.services.application import ApplicationServices


router = APIRouter(tags=["settings"])
security = HTTPBasic(auto_error=False)


def require_admin(
    request: Request,
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> ApplicationServices:
    app_services = services(request)
    expected = app_services.config.settings_admin_token
    submitted = credentials.password if credentials else ""
    if not expected or not secrets.compare_digest(submitted, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid settings credentials.",
        )
    return app_services


def masked_settings(app_services: ApplicationServices) -> dict[str, str]:
    values = {
        "GOOGLE_API_KEY": app_services.config.google_api_key,
        "QDRANT_URL": app_services.config.qdrant_url,
        "QDRANT_API_KEY": app_services.config.qdrant_api_key,
    }
    return app_services.settings.masked(values)


@router.get("/api/admin/settings")
def get_settings(
    app_services: ApplicationServices = Depends(require_admin),
):
    return {"settings": masked_settings(app_services)}


@router.put("/api/admin/settings")
def update_settings(
    update: RuntimeSettingsUpdate,
    app_services: ApplicationServices = Depends(require_admin),
):
    try:
        app_services.update_runtime_settings(update.present_values())
    except Exception as error:
        raise HTTPException(status_code=503, detail="Settings could not be saved.") from error
    return {"settings": masked_settings(app_services)}
