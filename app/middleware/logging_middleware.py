auth_service/app/middleware/logging_middleware.py
```
"""
Request Correlation and Request Logging Middleware

This middleware automatically sets a correlation ID for each request,
logs request/response information, and provides performance tracking.
"""

import time
import uuid
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import (
    get_logger,
    set_request_id,
    get_request_id,
    log_request,
    log_error as log_app_error,
)


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID and log requests."""

    def __init__(
        self,
        app,
        logger: Optional[logging.Logger] = None,
        enabled: bool = True,
    ):
        super().__init__(app)
        self.logger = logger or get_logger(__name__)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled:
            return await call_next(request)

        correlation_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        set_request_id(correlation_id)
        request.state.request_id = correlation_id

        self.logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "client_host": request.client.host if request.client else "unknown",
                }
            },
        )

        start_time = time.time()
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000

            log_request(
                self.logger,
                request.method,
                request.url.path,
                response.status_code,
                duration,
                client_host=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                correlation_id=correlation_id,
            )

            response.headers["X-Request-ID"] = correlation_id
            return response

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_app_error(
                self.logger,
                e,
                f"Error processing {request.method} {request.url.path}",
                duration_ms=duration,
                client_host=request.client.host if request.client else "unknown",
                correlation_id=correlation_id,
            )
            raise

    def __repr__(self) -> str:
        return f"<RequestCorrelationMiddleware enabled={self.enabled}>"
