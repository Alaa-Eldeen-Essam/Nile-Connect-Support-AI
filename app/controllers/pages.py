from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return request.app.state.templates.TemplateResponse(request, "index.html", {"title": "WE Telecom AI Agent"})


@router.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return request.app.state.templates.TemplateResponse(request, "privacy.html", {"title": "Privacy"})
