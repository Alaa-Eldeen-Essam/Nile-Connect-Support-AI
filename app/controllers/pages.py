from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.config import ROOT_DIR


router = APIRouter()


@router.get("/", response_class=FileResponse)
def home():
    return FileResponse(ROOT_DIR / "frontend_dist" / "index.html")
