"""RFC 7807 Problem Details Error Middleware for HomePilot Market Intelligence.

Standardizes all HTTP error responses to media type: application/problem+json
Aligned with the HomePilot Backend Architecture Specification:
- type: URI reference resolving the problem type
- title: Short, human-readable summary
- status: HTTP status code
- detail: Specific explanation of this occurrence
- instance: Relative URI of the request
- invalid_params: List of parameter validation failures
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict, Any, List

class RFC7807Exception(Exception):
    def __init__(self, status_code: int, title: str, detail: str, type_uri: str = "about:blank", invalid_params: List[Dict[str, Any]] = None):
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type_uri = type_uri
        self.invalid_params = invalid_params or []

def create_problem_response(
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    type_uri: str = "about:blank",
    invalid_params: List[Dict[str, Any]] = None
) -> JSONResponse:
    payload = {
        "type": type_uri,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
        "invalidParams": invalid_params or []
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json"
    )

async def rfc7807_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return create_problem_response(
        status_code=exc.status_code,
        title=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
        detail=str(exc.detail),
        instance=str(request.url.path),
        type_uri=f"https://homepilot.ie/errors/http-{exc.status_code}"
    )

async def rfc7807_validation_exception_handler(request: Request, exc: RequestValidationError):
    invalid_params = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        invalid_params.append({"name": loc, "reason": msg})

    return create_problem_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        title="Request Validation Failed",
        detail="The request payload failed schema validation constraints.",
        instance=str(request.url.path),
        type_uri="https://homepilot.ie/errors/validation-failed",
        invalid_params=invalid_params
    )

async def rfc7807_custom_exception_handler(request: Request, exc: RFC7807Exception):
    return create_problem_response(
        status_code=exc.status_code,
        title=exc.title,
        detail=exc.detail,
        instance=str(request.url.path),
        type_uri=exc.type_uri,
        invalid_params=exc.invalid_params
    )
