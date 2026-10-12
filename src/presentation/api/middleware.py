import logging

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from src.trace import TRACE_ID_HEADER, new_trace_id, reset_trace_id, set_trace_id

logger = logging.getLogger(__name__)


class TraceIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self._app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        trace_id = headers.get(TRACE_ID_HEADER) or new_trace_id()
        token = set_trace_id(trace_id)
        try:
            if scope["type"] == "http":
                logger.info("%s %s", scope["method"], scope["path"])
            await self._app(scope, receive, send)
        finally:
            reset_trace_id(token)
