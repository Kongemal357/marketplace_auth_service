from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
import pytest

from src.application.exceptions import InvalidRefreshTokenError
from src.application.usecases.refresh_token import RefreshToken
from tests.conftest import FakeUnitOfWork

JWT_SECRET = "test-secret-key-that-is-long-enough"
JWT_ALGORITHM = "HS256"


async def _create_user(fake_uow: FakeUnitOfWork, email: str) -> int:
    hashed = bcrypt.hashpw(b"pass", bcrypt.gensalt()).decode()
    user = await fake_uow.users.create(name="Test", email=email, password=hashed)
    return user.id


def _make_usecase(fake_uow: FakeUnitOfWork) -> RefreshToken:
    return RefreshToken(
        uow=fake_uow,
        jwt_secret=JWT_SECRET,
        jwt_algorithm=JWT_ALGORITHM,
        jwt_expire_hours=24,
        jwt_refresh_expire_days=30,
    )


def _make_refresh_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.now(UTC) + timedelta(days=30),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@pytest.mark.asyncio
async def test_refresh_returns_new_pair(fake_uow: FakeUnitOfWork) -> None:
    user_id = await _create_user(fake_uow, "alice@test.com")
    usecase = _make_usecase(fake_uow)
    token = _make_refresh_token(user_id)

    pair = await usecase.execute(token)

    assert pair.access_token
    assert pair.refresh_token

    access = jwt.decode(pair.access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert access["user_id"] == user_id
    assert access["type"] == "access"


@pytest.mark.asyncio
async def test_refresh_with_access_token_raises(fake_uow: FakeUnitOfWork) -> None:
    user_id = await _create_user(fake_uow, "alice@test.com")
    usecase = _make_usecase(fake_uow)

    access_token = jwt.encode(
        {
            "user_id": user_id,
            "email": "alice@test.com",
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(InvalidRefreshTokenError):
        await usecase.execute(access_token)


@pytest.mark.asyncio
async def test_refresh_with_invalid_token_raises(fake_uow: FakeUnitOfWork) -> None:
    usecase = _make_usecase(fake_uow)

    with pytest.raises(InvalidRefreshTokenError):
        await usecase.execute("garbage")


@pytest.mark.asyncio
async def test_refresh_with_expired_token_raises(fake_uow: FakeUnitOfWork) -> None:
    user_id = await _create_user(fake_uow, "alice@test.com")
    usecase = _make_usecase(fake_uow)

    expired = jwt.encode(
        {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.now(UTC) - timedelta(days=1),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(InvalidRefreshTokenError):
        await usecase.execute(expired)


@pytest.mark.asyncio
async def test_refresh_with_deleted_user_raises(fake_uow: FakeUnitOfWork) -> None:
    user_id = await _create_user(fake_uow, "alice@test.com")
    token = _make_refresh_token(user_id)
    await fake_uow.users.delete(user_id)
    usecase = _make_usecase(fake_uow)

    with pytest.raises(InvalidRefreshTokenError):
        await usecase.execute(token)
