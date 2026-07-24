from fastapi import Request

from app.services.application import ApplicationServices


def services(request: Request) -> ApplicationServices:
    return request.app.state.services
