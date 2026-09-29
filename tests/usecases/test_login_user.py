import bcrypt
import jwt
import pytest

from src.application.exceptions import InvalidCredentialsError
from src.application.usecases.login_user import LoginUser
from tests.conftest import FakeUnitOfWork

JWT_SECRET = "test-secret-key-that-is-long-enough"
JWT_ALGORITHM = "HS256"


async def _create_user(fake_uow: FakeUnitOfWork, email: str, password: str) -> None:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    await fake_uow.users.create(name="Test", email=email, password=hashed)


def _make_usecase(fake_uow: FakeUnitOfWork) -> LoginUser:
    return LoginUser(
        uow=fake_uow,
        jwt_secret=JWT_SECRET,
        jwt_algorithm=JWT_ALGORITHM,
        jwt_expire_hours=24,
        jwt_refresh_expire_days=30,
    )


@pytest.mark.asyncio
async def test_login_returns_token_pair(fake_uow: FakeUnitOfWork) -> None:
    await _create_user(fake_uow, "alice@test.com", "securepass")
    usecase = _make_usecase(fake_uow)

    pair = await usecase.execute(email="alice@test.com", password="securepass")

    assert pair.access_token
    assert pair.refresh_token

    access = jwt.decode(pair.access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert access["user_id"] == 1
    assert access["email"] == "alice@test.com"
    assert access["type"] == "access"

    refresh = jwt.decode(pair.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert refresh["user_id"] == 1
    assert refresh["type"] == "refresh"


@pytest.mark.asyncio
async def test_login_wrong_email_raises(fake_uow: FakeUnitOfWork) -> None:
    await _create_user(fake_uow, "alice@test.com", "securepass")
    usecase = _make_usecase(fake_uow)

    with pytest.raises(InvalidCredentialsError):
        await usecase.execute(email="wrong@test.com", password="securepass")


@pytest.mark.asyncio
async def test_login_wrong_password_raises(fake_uow: FakeUnitOfWork) -> None:
    await _create_user(fake_uow, "alice@test.com", "securepass")
    usecase = _make_usecase(fake_uow)

    with pytest.raises(InvalidCredentialsError):
        await usecase.execute(email="alice@test.com", password="wrongpass")
