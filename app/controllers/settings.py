from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.dependencies import services
from app.models.schemas import RuntimeSettingsUpdate
from app.services.application import ApplicationServices


router = APIRouter(tags=["settings"])
security = HTTPBasic()


def require_admin(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
) -> ApplicationServices:
    app_services = services(request)
    expected = app_services.config.settings_admin_token
    if not expected or not secrets.compare_digest(credentials.password, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid settings credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return app_services


@router.get("/settings", response_class=HTMLResponse)
def settings_page(
    request: Request,
    app_services: ApplicationServices = Depends(require_admin),
):
    values = {
        "GOOGLE_API_KEY": app_services.config.google_api_key,
        "QDRANT_URL": app_services.config.qdrant_url,
        "QDRANT_API_KEY": app_services.config.qdrant_api_key,
    }
    return request.app.state.templates.TemplateResponse(
        request,
        "settings.html",
        {
            "title": "Runtime settings",
            "settings": app_services.settings.masked(
                values
            ),
        },
    )


@router.post("/settings")
async def update_settings(
    request: Request,
    app_services: ApplicationServices = Depends(require_admin),
):
    form = await request.form()
    update = RuntimeSettingsUpdate(
        GOOGLE_API_KEY=form.get("GOOGLE_API_KEY") or None,
        QDRANT_URL=form.get("QDRANT_URL") or None,
        QDRANT_API_KEY=form.get("QDRANT_API_KEY") or None,
    )
    try:
        app_services.update_runtime_settings(update.present_values())
    except Exception as error:
        raise HTTPException(status_code=503, detail="Settings could not be saved.") from error
    return RedirectResponse("/settings", status_code=303)
