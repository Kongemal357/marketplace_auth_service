import logging

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.logging_config import TraceIdFilter
from src.presentation.api.middleware import TraceIdMiddleware
from src.trace import get_trace_id, new_trace_id, reset_trace_id, set_trace_id


def test_set_and_reset_trace_id() -> None:
    assert get_trace_id() is None

    token = set_trace_id("abc")
    assert get_trace_id() == "abc"

    reset_trace_id(token)
    assert get_trace_id() is None


def test_new_trace_id_is_unique() -> None:
    assert new_trace_id() != new_trace_id()


def test_trace_filter_defaults_to_dash() -> None:
    record = logging.LogRecord("x", logging.INFO, "path", 1, "msg", (), None)

    TraceIdFilter().filter(record)

    assert record.trace_id == "-"


def test_trace_filter_uses_contextvar() -> None:
    token = set_trace_id("abc")
    try:
        record = logging.LogRecord("x", logging.INFO, "path", 1, "msg", (), None)
        TraceIdFilter().filter(record)
        assert record.trace_id == "abc"
    finally:
        reset_trace_id(token)


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(TraceIdMiddleware)

    @app.get("/ping")
    async def ping() -> dict[str, str | None]:
        return {"trace_id": get_trace_id()}

    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_middleware_uses_incoming_header(client: AsyncClient) -> None:
    resp = await client.get("/ping", headers={"X-Trace-Id": "trace-42"})

    assert resp.json() == {"trace_id": "trace-42"}


async def test_middleware_generates_trace_id(client: AsyncClient) -> None:
    resp = await client.get("/ping")

    assert resp.json()["trace_id"]


async def test_middleware_resets_after_request(client: AsyncClient) -> None:
    await client.get("/ping", headers={"X-Trace-Id": "trace-42"})

    assert get_trace_id() is None
