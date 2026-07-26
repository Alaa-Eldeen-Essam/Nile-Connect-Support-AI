from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response

from app.dependencies import services
from app.models.schemas import ChatRequest, ChatResponse
from app.services.application import ApplicationServices

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)


def session_id(request: Request) -> str:
    return request.cookies.get("we_session") or str(uuid.uuid4())


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    app_services: ApplicationServices = Depends(services),
):
    current_session = session_id(request)
    try:
        reply = await run_in_threadpool(
            app_services.agent.reply, payload.message.strip(), current_session
        )
    except RuntimeError as error:
        logger.warning("Chat request rejected: %s", error)
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=503, detail="The agent service is temporarily unavailable."
        ) from error
    response = JSONResponse(ChatResponse(reply=reply).model_dump())
    response.set_cookie(
        "we_session",
        current_session,
        httponly=True,
        secure=app_services.config.is_production,
        samesite="lax",
        max_age=60 * 60 * 24,
    )
    return response


@router.post("/reset", status_code=204)
def reset(
    request: Request,
    app_services: ApplicationServices = Depends(services),
):
    old_session = request.cookies.get("we_session")
    if old_session:
        try:
            app_services.mongo.database["chat_history"].delete_many({"SessionId": old_session})
        except Exception:
            pass
    response = Response(status_code=204)
    response.delete_cookie("we_session")
    return response
